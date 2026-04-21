import time
import threading
from typing import Optional, Dict, Tuple
from collections import deque

from src.models.state import State
from src.models.kb import KnowledgeBase
from src.models.board import Board
from src.logic.grounding import ground_axioms
from gui.bridge import InputData, OutputData

class ForwardChainingSolver:
    """
    Forward chaining solver adapted for the GUI.
    Handles KB generation and grounding internally.
    """

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.start_time = 0.0

    def solve(self, input_data: InputData, stop_event: threading.Event = None) -> OutputData:
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

        # 3. Run Forward Chaining Logic
        result_state = self._forward_chaining_core(initial_state, kb, stop_event)

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

            # Check if the board is fully solved (no 0s left)
            is_complete = all(cell != 0 for row in solution_matrix for cell in row)

            if is_complete:
                return OutputData(
                    status='success',
                    solution=solution_matrix,
                    stats={
                        'time_ms': round(solve_time_ms, 2),
                        'clauses_generated': len(kb.clauses),
                        'algorithm': 'Forward Chaining'
                    },
                    message="Solved successfully via Unit Propagation!"
                )
            else:
                return OutputData(
                    status='unsolvable',
                    solution=solution_matrix,
                    stats={
                        'time_ms': round(solve_time_ms, 2),
                        'clauses_generated': len(kb.clauses),
                        'algorithm': 'Forward Chaining (Partial)'
                    },
                    message="Forward Chaining stopped. Pure logic/unit propagation is not enough to fully solve this complex grid without a backtracking phase. Displaying partial progress."
                )
        else:
            # THE MISSING PIECE: What to do when the puzzle is a true contradiction
            return OutputData(
                status='unsolvable',
                solution=None,
                stats={
                    'time_ms': round(solve_time_ms, 2),
                    'clauses_generated': len(kb.clauses),
                    'algorithm': 'Forward Chaining'
                },
                message="No logical solution exists. The constraints contradict each other."
            )

    def _forward_chaining_core(self, initial_state: State, kb: KnowledgeBase, stop_event: threading.Event) -> Optional[State]:
        if not kb.clauses:
            return initial_state

        N = kb.N
        var_to_cell: Dict[int, Tuple[int, int, int]] = {}
        for r in range(1, N + 1):
            for c in range(1, N + 1):
                for v in range(1, N + 1):
                    var_id = kb.get_var_id(r, c, v)
                    var_to_cell[var_id] = (r, c, v)

        unit_clauses = kb.get_unit_clauses()
        agenda = deque(unit_clauses)
        inferences = {}

        clauses_list = [list(clause) for clause in kb.clauses]
        satisfied = [False] * len(clauses_list)
        active_clauses = set(range(len(clauses_list)))

        iteration_count = 0

        while agenda:
            # Periodic cancellation check
            iteration_count += 1
            if iteration_count % 100 == 0 and stop_event and stop_event.is_set():
                return None

            p = agenda.popleft()

            if p in inferences: continue
            inferences[p] = True

            for i in list(active_clauses):
                clause = clauses_list[i]

                if p in clause:
                    satisfied[i] = True
                    active_clauses.discard(i)
                    continue

                if -p in clause:
                    clause.remove(-p)
                    if len(clause) == 0:
                        return None
                    if len(clause) == 1:
                        unit_lit = clause[0]
                        if unit_lit not in inferences and -unit_lit not in inferences:
                            agenda.append(unit_lit)

        board = [[0] * N for _ in range(N)]
        for var_id in inferences:
            if var_id > 0:
                if var_id in var_to_cell:
                    r, c, v = var_to_cell[var_id]
                    board[r - 1][c - 1] = v

        return State(tuple(tuple(row) for row in board), initial_state.puzzle_ref)
