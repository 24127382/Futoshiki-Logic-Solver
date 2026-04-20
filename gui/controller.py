"""
Controller Module: GUI <-> Solver Communication Hub
=====================================================
Coordinates everything that sits between the user clicking buttons and
the solvers in ``src/solvers``. Runs solves in a background thread so the
UI stays responsive, and reports progress via a ``update_callback``.
"""

from __future__ import annotations

import sys
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

_ROOT = Path(__file__).parent.parent
for p in (_ROOT, _ROOT / "src"):
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)


class SolverType(str, Enum):
    BACKTRACKING = "Backtracking"
    FORWARD_CHAINING = "Forward Chaining"
    A_STAR = "A*"


class SolveStatus(str, Enum):
    IDLE = "idle"
    SOLVING = "solving"
    SUCCESS = "success"
    UNSOLVABLE = "unsolvable"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class SolveResult:
    status: SolveStatus
    solution: Optional[List[List[int]]] = None
    elapsed: float = 0.0
    nodes: int = 0
    message: str = ""


class FutoshikiController:
    """Mediates between the GUI and the solver algorithms."""

    def __init__(self, update_callback=None) -> None:
        self.update_callback = update_callback or (lambda s, d: None)
        self.timeout_seconds: int = 30
        self.is_solving: bool = False
        self._cancel_flag = threading.Event()
        self._solver_thread = None
        self.last_result: Optional[SolveResult] = None

    def set_timeout(self, seconds: int) -> None:
        if seconds > 0:
            self.timeout_seconds = seconds

    def cancel_solve(self) -> None:
        self._cancel_flag.set()

    def handle_solve_request(
        self,
        gui_matrix: List[List[str]],
        gui_constraints: Dict[str, str],
        size: int,
        algorithm: str,
    ) -> None:
        if self.is_solving:
            self.update_callback("error", {"message": "Solver is already running."})
            return

        try:
            matrix = self._gui_to_int_matrix(gui_matrix, size)
        except ValueError as e:
            self.update_callback("error", {"message": "Invalid cell value: " + str(e)})
            return

        constraints = self._gui_to_constraints(gui_constraints)

        conflicts = self._find_conflicts(matrix, constraints, size)
        if conflicts:
            self.update_callback(
                "error",
                {
                    "message": "Initial grid violates row/column/inequality rules.",
                    "conflict_cells": conflicts,
                },
            )
            return

        self.is_solving = True
        self._cancel_flag.clear()
        self.update_callback("solving", {"algorithm": algorithm})

        thread = threading.Thread(
            target=self._solve_worker,
            args=(matrix, constraints, size, algorithm),
            daemon=True,
        )
        self._solver_thread = thread
        thread.start()

    def _solve_worker(self, matrix, constraints, size, algorithm) -> None:
        start = time.time()
        result: SolveResult

        try:
            board = self._build_board(matrix, constraints, size)
            container = {"done": False, "out": None, "error": None, "nodes": 0}

            def run():
                try:
                    if algorithm == SolverType.BACKTRACKING.value:
                        solver, solution = self._run_backtracking(board)
                        container["nodes"] = solver.nodes_visited
                        container["out"] = solution
                    elif algorithm == SolverType.FORWARD_CHAINING.value:
                        solution, nodes = self._run_forward_chaining(board)
                        container["nodes"] = nodes
                        container["out"] = solution
                    elif algorithm == SolverType.A_STAR.value:
                        solution, nodes = self._run_a_star(board)
                        container["nodes"] = nodes
                        container["out"] = solution
                    else:
                        raise ValueError("Unknown algorithm: " + algorithm)
                except Exception as e:
                    container["error"] = e
                finally:
                    container["done"] = True

            worker = threading.Thread(target=run, daemon=True)
            worker.start()
            deadline = start + self.timeout_seconds
            while time.time() < deadline and not container["done"]:
                if self._cancel_flag.is_set():
                    break
                time.sleep(0.05)

            elapsed = time.time() - start

            if self._cancel_flag.is_set():
                result = SolveResult(SolveStatus.CANCELLED, elapsed=elapsed,
                                     message="Cancelled by user.")
            elif not container["done"]:
                result = SolveResult(
                    SolveStatus.TIMEOUT,
                    elapsed=elapsed,
                    message="Timed out after " + str(self.timeout_seconds) + "s.",
                )
            elif container["error"] is not None:
                result = SolveResult(
                    SolveStatus.ERROR,
                    elapsed=elapsed,
                    message=str(container["error"]),
                )
            elif container["out"] is None:
                result = SolveResult(
                    SolveStatus.UNSOLVABLE,
                    elapsed=elapsed,
                    nodes=container["nodes"],
                    message="No solution found.",
                )
            else:
                solution_list = self._to_matrix(container["out"])
                result = SolveResult(
                    SolveStatus.SUCCESS,
                    solution=solution_list,
                    elapsed=elapsed,
                    nodes=container["nodes"],
                    message="Solved successfully.",
                )
        except Exception as e:
            result = SolveResult(
                SolveStatus.ERROR,
                elapsed=time.time() - start,
                message=type(e).__name__ + ": " + str(e),
            )

        self.last_result = result
        self.is_solving = False

        self.update_callback(
            result.status.value,
            {
                "solution": result.solution,
                "elapsed": result.elapsed,
                "nodes": result.nodes,
                "message": result.message,
                "algorithm": algorithm,
            },
        )

    def _run_backtracking(self, board):
        from src.solvers.backtracking import BacktrackingSolver
        solver = BacktrackingSolver()
        solution = solver.solve(board)
        return solver, solution

    def _run_forward_chaining(self, board):
        from src.models.kb import KnowledgeBase
        from src.logic.grounding import ground_axioms
        from src.solvers.forward_chaining import forward_chaining_solver

        kb = KnowledgeBase(board.N)
        ground_axioms(kb, board)
        initial_state = board.initial_state
        state = forward_chaining_solver(initial_state, kb)
        nodes = len(kb.clauses)
        if state is None:
            return None, nodes
        return state.board, nodes

    def _run_a_star(self, board):
        try:
            from src.solvers.a_star import a_star_solver
        except ImportError as e:
            raise RuntimeError("A* solver not available: " + str(e))

        initial_state = board.initial_state
        try:
            state = a_star_solver(initial_state, board)
        except TypeError:
            state = a_star_solver(initial_state)

        if state is None:
            return None, 0
        if hasattr(state, "board"):
            return state.board, 0
        return state, 0

    def _build_board(self, matrix, constraints, size):
        from src.models.board import Board
        from src.models.state import State

        board_tuple = tuple(tuple(row) for row in matrix)
        initial_state = State(board_tuple, None)
        cons_tuple = tuple(constraints)
        return Board(size, initial_state, cons_tuple)

    @staticmethod
    def _gui_to_int_matrix(gui_matrix, size):
        if len(gui_matrix) != size:
            raise ValueError("Matrix has " + str(len(gui_matrix)) + " rows, expected " + str(size))
        matrix = []
        for r, row in enumerate(gui_matrix):
            if len(row) != size:
                raise ValueError("Row " + str(r) + " has " + str(len(row)) + " cells, expected " + str(size))
            int_row = []
            for c, cell in enumerate(row):
                if cell == "":
                    int_row.append(0)
                else:
                    try:
                        v = int(cell)
                    except ValueError:
                        raise ValueError("cell (" + str(r) + "," + str(c) + ") = " + repr(cell))
                    if not (1 <= v <= size):
                        raise ValueError("cell (" + str(r) + "," + str(c) + ") = " + str(v) + " out of 1.." + str(size))
                    int_row.append(v)
            matrix.append(int_row)
        return matrix

    @staticmethod
    def _gui_to_constraints(gui_constraints):
        out = []
        for key, sign in gui_constraints.items():
            try:
                left, right = key.split("-")
                r1, c1 = map(int, left.strip("()").split(","))
                r2, c2 = map(int, right.strip("()").split(","))
            except (ValueError, IndexError):
                continue
            if sign not in ("<", ">"):
                continue
            out.append((r1, c1, sign, r2, c2))
        return out

    @staticmethod
    def _to_matrix(board):
        if hasattr(board, "board"):
            board = board.board
        return [list(row) for row in board]

    @staticmethod
    def _find_conflicts(matrix, constraints, size):
        conflicts = set()

        for r in range(size):
            seen = {}
            for c in range(size):
                v = matrix[r][c]
                if v == 0:
                    continue
                if v in seen:
                    conflicts.add((r, c))
                    conflicts.add((r, seen[v]))
                else:
                    seen[v] = c

        for c in range(size):
            seen = {}
            for r in range(size):
                v = matrix[r][c]
                if v == 0:
                    continue
                if v in seen:
                    conflicts.add((r, c))
                    conflicts.add((seen[v], c))
                else:
                    seen[v] = r

        for r1, c1, op, r2, c2 in constraints:
            v1 = matrix[r1][c1]
            v2 = matrix[r2][c2]
            if v1 == 0 or v2 == 0:
                continue
            if (op == "<" and not (v1 < v2)) or (op == ">" and not (v1 > v2)):
                conflicts.add((r1, c1))
                conflicts.add((r2, c2))

        return sorted(conflicts)

    def load_puzzle_from_file(self, filepath):
        from src.utils.parser import load_puzzle_file

        board, state = load_puzzle_file(filepath)
        size = board.N
        matrix = [list(row) for row in state.board]

        constraints_gui = {}
        for (r1, c1, op, r2, c2) in board.constraints:
            if (r1, c1) > (r2, c2):
                r1, c1, r2, c2 = r2, c2, r1, c1
                op = ">" if op == "<" else "<"
            constraints_gui["(" + str(r1) + "," + str(c1) + ")-(" + str(r2) + "," + str(c2) + ")"] = op

        return matrix, constraints_gui, size

    def save_puzzle_to_file(self, filepath, matrix, constraints_gui, size):
        lines = [str(size), ""]

        for row in matrix:
            lines.append(", ".join(str(v) for v in row))
        lines.append("")

        h_table = [[0] * (size - 1) for _ in range(size)]
        v_table = [[0] * size for _ in range(size - 1)]

        for key, sign in constraints_gui.items():
            try:
                left, right = key.split("-")
                r1, c1 = map(int, left.strip("()").split(","))
                r2, c2 = map(int, right.strip("()").split(","))
            except (ValueError, IndexError):
                continue

            if r1 == r2:
                if c1 > c2:
                    r1, c1, r2, c2 = r2, c2, r1, c1
                    sign = ">" if sign == "<" else "<"
                h_table[r1][c1] = 1 if sign == "<" else -1
            elif c1 == c2:
                if r1 > r2:
                    r1, c1, r2, c2 = r2, c2, r1, c1
                    sign = ">" if sign == "<" else "<"
                v_table[r1][c1] = 1 if sign == "<" else -1

        for row in h_table:
            lines.append(", ".join(str(v) for v in row))
        lines.append("")
        for row in v_table:
            lines.append(", ".join(str(v) for v in row))

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
