"""A* solver for Futoshiki puzzles.

This implementation is constraint-aware:
- Prunes row/column duplicate violations early
- Enforces inequality constraints during expansion
- Uses MRV-style cell ordering to reduce branching
"""

from __future__ import annotations

import time
import threading
from heapq import heappop, heappush
from itertools import count
from typing import List, Optional, Tuple

from src.models.board import Board
from src.models.state import State
from src.utils.heuristic import get_heuristic
from gui.bridge import InputData, OutputData


class A_StarSolver:
	"""
	A* solver adapted for the GUI.
	Uses heuristic-guided search with constraint validation.
	"""

	def __init__(self, timeout: float = 30.0):
		self.timeout = timeout
		self.start_time = 0.0
		self.nodes_visited = 0

	def solve(self, input_data: InputData, stop_event: threading.Event = None) -> OutputData:
		"""
		Solve a Futoshiki puzzle using A* search.
		
		Args:
			input_data: Puzzle data (size, matrix, constraints)
			stop_event: Threading event to signal timeout
			
		Returns:
			OutputData with solution status and results
		"""
		self.start_time = time.time()
		self.nodes_visited = 0
		N = input_data.size

		# 1. Setup Models
		initial_board = tuple(tuple(row) for row in input_data.matrix)
		initial_state = State(initial_board)

		# Convert GUI constraints: ((r1, c1), (r2, c2), op) -> (r1, c1, op, r2, c2)
		solver_constraints = []
		for (r1, c1), (r2, c2), op in input_data.constraints:
			solver_constraints.append((r1, c1, op, r2, c2))

		board = Board(N, initial_state, tuple(solver_constraints))

		# 2. Run A* solver
		result_state, nodes = a_star_solver(initial_state, board, stop_event=stop_event)
		self.nodes_visited = nodes

		solve_time_ms = (time.time() - self.start_time) * 1000

		# Handle cancellation/timeout
		if stop_event and stop_event.is_set():
			return OutputData(
				status='timeout',
				solution=None,
				stats={'time_ms': round(solve_time_ms, 2), 'nodes_visited': self.nodes_visited},
				message="Solver timed out or was cancelled."
			)

		# Handle completion
		if result_state:
			solution_matrix = [list(row) for row in result_state.board]
			return OutputData(
				status='success',
				solution=solution_matrix,
				stats={
					'time_ms': round(solve_time_ms, 2),
					'nodes_visited': self.nodes_visited,
					'algorithm': 'A*'
				},
				message="Puzzle solved successfully with A* search!"
			)
		else:
			return OutputData(
				status='unsolvable',
				solution=None,
				stats={
					'time_ms': round(solve_time_ms, 2),
					'nodes_visited': self.nodes_visited,
					'algorithm': 'A*'
				},
				message="No solution exists for this puzzle."
			)


def a_star_solver(
	initial_state: State, board: Board, heuristic_name: str = "advanced", stop_event: threading.Event = None
) -> Tuple[Optional[State], int]:
	"""Solve a puzzle using A* search.

	Args:
		initial_state: Starting puzzle state.
		board: Puzzle definition with board size and constraints.

	Returns:
		Solved state if found, otherwise None, and nodes visited.
	"""
	start = State(initial_state.board, board)
	heuristic_fn = get_heuristic(heuristic_name)
	if not _is_partial_valid(start.board, board):
		return None, 0

	queue: List[Tuple[int, int, int, State]] = []
	ticket = count()
	nodes_visited = 0

	start_g = _filled_cells(start.board)
	start_h = heuristic_fn(start, board)
	heappush(queue, (start_g + start_h, start_h, next(ticket), start))

	best_g = {start: start_g}

	while queue:
		if stop_event and stop_event.is_set():
			return None, nodes_visited
		_, _, _, current = heappop(queue)
		nodes_visited += 1

		if current.is_complete() and _is_partial_valid(current.board, board):
			return State(current.board, board), nodes_visited

		current_g = best_g.get(current)
		if current_g is None:
			continue

		row, col = _select_unassigned_cell(current.board, board)
		if row == -1:
			continue

		for value in _ordered_domain_values(current.board, board, row, col):
			next_board = _assign(current.board, row, col, value)
			if not _is_partial_valid(next_board, board):
				continue

			next_state = State(next_board, board)
			next_g = current_g + 1

			if next_g >= best_g.get(next_state, 10**18):
				continue

			best_g[next_state] = next_g
			next_h = heuristic_fn(next_state, board)
			heappush(queue, (next_g + next_h, next_h, next(ticket), next_state))

	return None, nodes_visited


def _filled_cells(grid: Tuple[Tuple[int, ...], ...]) -> int:
	return sum(1 for row in grid for value in row if value != 0)


def _assign(
	grid: Tuple[Tuple[int, ...], ...], row: int, col: int, value: int
) -> Tuple[Tuple[int, ...], ...]:
	temp = [list(r) for r in grid]
	temp[row][col] = value
	return tuple(tuple(r) for r in temp)


def _select_unassigned_cell(grid: Tuple[Tuple[int, ...], ...], board: Board) -> Tuple[int, int]:
	"""Pick an empty cell using MRV (minimum remaining values)."""
	best_pos = (-1, -1)
	best_domain = 10**9

	for r in range(board.N):
		for c in range(board.N):
			if grid[r][c] != 0:
				continue

			domain_size = len(_ordered_domain_values(grid, board, r, c))
			if domain_size < best_domain:
				best_domain = domain_size
				best_pos = (r, c)

			if best_domain == 1:
				return best_pos

	return best_pos


def _ordered_domain_values(
	grid: Tuple[Tuple[int, ...], ...], board: Board, row: int, col: int
) -> List[int]:
	values = []
	for value in range(1, board.N + 1):
		if _is_value_allowed(grid, board, row, col, value):
			values.append(value)
	return values


def _is_value_allowed(
	grid: Tuple[Tuple[int, ...], ...], board: Board, row: int, col: int, value: int
) -> bool:
	if value in grid[row]:
		return False

	for r in range(board.N):
		if grid[r][col] == value:
			return False

	temp = [list(r) for r in grid]
	temp[row][col] = value
	return _inequalities_hold_partial(tuple(tuple(r) for r in temp), board)


def _domain_heuristic(grid: Tuple[Tuple[int, ...], ...], board: Board) -> int:
	"""Estimate effort: sum of branching options for remaining cells.

	Returns a large value when contradiction is detected (empty domain).
	"""
	score = 0
	for r in range(board.N):
		for c in range(board.N):
			if grid[r][c] != 0:
				continue

			options = len(_ordered_domain_values(grid, board, r, c))
			if options == 0:
				return 10**9
			score += options - 1
	return score


def _is_partial_valid(grid: Tuple[Tuple[int, ...], ...], board: Board) -> bool:
	for r in range(board.N):
		row_vals = [v for v in grid[r] if v != 0]
		if len(row_vals) != len(set(row_vals)):
			return False

	for c in range(board.N):
		col_vals = [grid[r][c] for r in range(board.N) if grid[r][c] != 0]
		if len(col_vals) != len(set(col_vals)):
			return False

	return _inequalities_hold_partial(grid, board)


def _inequalities_hold_partial(grid: Tuple[Tuple[int, ...], ...], board: Board) -> bool:
	if not board.constraints:
		return True

	for constraint in board.constraints:
		if len(constraint) == 3:
			r1, c1, op = constraint
			r2, c2 = r1, c1 + 1
		elif len(constraint) == 5:
			r1, c1, op, r2, c2 = constraint
		else:
			return False

		# Constraints are 0-based from the parser
		# Check bounds to handle both test cases and real data
		if r1 < 0 or c1 < 0 or r2 < 0 or c2 < 0 or r1 >= len(grid) or c1 >= len(grid[0]) or r2 >= len(grid) or c2 >= len(grid[0]):
			# Out of bounds constraint - assume it's invalid and skip
			continue
		
		left = grid[r1][c1]
		right = grid[r2][c2]

		if left == 0 or right == 0:
			continue

		if op == '<' and not (left < right):
			return False
		if op == '>' and not (left > right):
			return False

	return True
