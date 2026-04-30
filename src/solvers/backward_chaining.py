"""Backward chaining solver for Futoshiki puzzles.

Implements a SAT-style backward search using DPLL on grounded CNF clauses.
Input State: Initial board configuration as a State object
Output State: Solved board configuration as a State object, or None if unsolvable
"""

from __future__ import annotations

import time
import threading
from typing import Dict, Iterable, List, Optional, Set, Tuple

from src.models.kb import KnowledgeBase
from src.models.state import State
from src.models.board import Board
from src.logic.grounding import ground_axioms
from gui.bridge import InputData, OutputData


Clause = Tuple[int, ...]
Assignment = Dict[int, bool]


def backward_chaining_solver(initial_state: State, kb: KnowledgeBase, stop_event: threading.Event = None) -> Optional[State]:
	"""Solve a grounded Futoshiki CNF by backward chaining (DPLL).

	Args:
		initial_state: Starting puzzle state.
		kb: Knowledge base containing CNF clauses.

	Returns:
		Solved state if satisfiable, otherwise None.
	"""
	if not kb.clauses:
		return initial_state

	clauses: List[Clause] = [tuple(clause) for clause in kb.clauses]
	model = _dpll(clauses, {}, stop_event)
	if model is None:
		return None

	return _build_state_from_model(initial_state, kb.N, model)


def _dpll(clauses: List[Clause], assignment: Assignment, stop_event: threading.Event = None) -> Optional[Assignment]:
	if stop_event and stop_event.is_set():
		return None
	# Apply deterministic simplifications first.
	ok, assignment = _unit_propagate(clauses, assignment)
	if not ok:
		return None

	ok, assignment = _eliminate_pure_literals(clauses, assignment)
	if not ok:
		return None

	if _all_clauses_satisfied(clauses, assignment):
		return assignment

	if _has_contradiction(clauses, assignment):
		return None

	branch_var = _choose_branch_variable(clauses, assignment)
	if branch_var is None:
		return assignment

	# Try True then False for deterministic behavior.
	for value in (True, False):
		next_assignment = dict(assignment)
		next_assignment[branch_var] = value
		result = _dpll(clauses, next_assignment, stop_event)
		if result is not None:
			return result

	return None


def _unit_propagate(clauses: Iterable[Clause], assignment: Assignment) -> Tuple[bool, Assignment]:
	assignment = dict(assignment)

	changed = True
	while changed:
		changed = False

		for clause in clauses:
			status, unit_lit = _clause_status_and_unit_literal(clause, assignment)

			if status == "unsatisfied":
				return False, assignment

			if status == "unit" and unit_lit is not None:
				var = abs(unit_lit)
				value = unit_lit > 0

				if var in assignment and assignment[var] != value:
					return False, assignment

				if var not in assignment:
					assignment[var] = value
					changed = True

	return True, assignment


def _eliminate_pure_literals(clauses: Iterable[Clause], assignment: Assignment) -> Tuple[bool, Assignment]:
	assignment = dict(assignment)

	polarity: Dict[int, int] = {}
	for clause in clauses:
		clause_true = False
		for lit in clause:
			lit_value = _literal_value(lit, assignment)
			if lit_value is True:
				clause_true = True
				break

		if clause_true:
			continue

		for lit in clause:
			var = abs(lit)
			if var in assignment:
				continue

			sign = 1 if lit > 0 else -1
			if var not in polarity:
				polarity[var] = sign
			elif polarity[var] != sign:
				polarity[var] = 0

	for var, sign in polarity.items():
		if sign == 0:
			continue

		value = sign > 0
		if var in assignment and assignment[var] != value:
			return False, assignment
		assignment[var] = value

	return True, assignment


def _all_clauses_satisfied(clauses: Iterable[Clause], assignment: Assignment) -> bool:
	for clause in clauses:
		if not any(_literal_value(lit, assignment) is True for lit in clause):
			return False
	return True


def _has_contradiction(clauses: Iterable[Clause], assignment: Assignment) -> bool:
	for clause in clauses:
		any_true = False
		any_unassigned = False
		for lit in clause:
			value = _literal_value(lit, assignment)
			if value is True:
				any_true = True
				break
			if value is None:
				any_unassigned = True

		if not any_true and not any_unassigned:
			return True

	return False


def _choose_branch_variable(clauses: Iterable[Clause], assignment: Assignment) -> Optional[int]:
	counts: Dict[int, int] = {}

	for clause in clauses:
		if any(_literal_value(lit, assignment) is True for lit in clause):
			continue

		for lit in clause:
			var = abs(lit)
			if var in assignment:
				continue
			counts[var] = counts.get(var, 0) + 1

	if not counts:
		return None

	return max(counts, key=counts.get)


def _clause_status_and_unit_literal(clause: Clause, assignment: Assignment) -> Tuple[str, Optional[int]]:
	"""Return one of: satisfied, unsatisfied, unresolved, unit."""
	unassigned_literals: List[int] = []

	for lit in clause:
		value = _literal_value(lit, assignment)
		if value is True:
			return "satisfied", None
		if value is None:
			unassigned_literals.append(lit)

	if not unassigned_literals:
		return "unsatisfied", None

	if len(unassigned_literals) == 1:
		return "unit", unassigned_literals[0]

	return "unresolved", None


def _literal_value(lit: int, assignment: Assignment) -> Optional[bool]:
	var = abs(lit)
	if var not in assignment:
		return None

	var_value = assignment[var]
	return var_value if lit > 0 else not var_value


def _build_state_from_model(initial_state: State, size: int, assignment: Assignment) -> Optional[State]:
	# Start from initial values and fill cells from the SAT model.
	board = [list(row) for row in initial_state.board]

	for var, is_true in assignment.items():
		if not is_true:
			continue

		row, col, value = _decode_var_id(var, size)
		existing = board[row][col]
		if existing != 0 and existing != value:
			return None
		board[row][col] = value

	if any(cell == 0 for row in board for cell in row):
		# A partial model is not enough to produce a valid solved board.
		return None

	solved_board = tuple(tuple(row) for row in board)
	return State(solved_board, initial_state.puzzle_ref)


def _decode_var_id(var_id: int, size: int) -> Tuple[int, int, int]:
	"""Inverse of KnowledgeBase.get_var_id, returning 0-based (row, col, value)."""
	base = size * size
	index = var_id - 1
	row = index // base
	rem = index % base
	col = rem // size
	value = (rem % size) + 1
	return row, col, value


class BackwardChainingSolver:
	"""
	Backward chaining solver adapted for the GUI.
	Uses DPLL SAT solver on grounded CNF clauses.
	"""

	def __init__(self, timeout: float = 30.0):
		self.timeout = timeout
		self.start_time = 0.0

	def solve(self, input_data: InputData, stop_event: threading.Event = None) -> OutputData:
		"""
		Solve a Futoshiki puzzle using backward chaining (DPLL).
		
		Args:
			input_data: Puzzle data (size, matrix, constraints)
			stop_event: Threading event to signal timeout
			
		Returns:
			OutputData with solution status and results
		"""
		self.start_time = time.time()
		N = input_data.size

		# 1. Setup Models
		initial_board = tuple(tuple(row) for row in input_data.matrix)
		initial_state = State(initial_board)

		# Convert GUI constraints: ((r1, c1), (r2, c2), op) -> (r1, c1, op, r2, c2)
		solver_constraints = []
		for (r1, c1), (r2, c2), op in input_data.constraints:
			solver_constraints.append((r1, c1, op, r2, c2))

		board = Board(N, initial_state, tuple(solver_constraints))
		kb = KnowledgeBase(N)

		# 2. Ground Axioms
		ground_axioms(kb, board)

		# 3. Run Backward Chaining (DPLL)
		result_state = backward_chaining_solver(initial_state, kb, stop_event=stop_event)

		solve_time_ms = (time.time() - self.start_time) * 1000

		# Handle cancellation/timeout
		if stop_event and stop_event.is_set():
			return OutputData(
				status='timeout',
				solution=None,
				stats={'time_ms': round(solve_time_ms, 2), 'clauses_generated': len(kb.clauses)},
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
					'clauses_generated': len(kb.clauses),
					'algorithm': 'Backward Chaining (DPLL)'
				},
				message="Puzzle solved successfully with backward chaining!"
			)
		else:
			return OutputData(
				status='unsolvable',
				solution=None,
				stats={
					'time_ms': round(solve_time_ms, 2),
					'clauses_generated': len(kb.clauses),
					'algorithm': 'Backward Chaining (DPLL)'
				},
				message="No solution exists for this puzzle."
			)
