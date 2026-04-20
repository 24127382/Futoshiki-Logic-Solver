"""
Controller Module: GUI ↔ Solver Communication Hub
===================================================
This module mediates between the tkinter GUI and the solver algorithms.
"""

import threading
import time
from typing import Dict, List, Callable, Optional, Tuple
from enum import Enum
import sys
from pathlib import Path

# Add src/ to path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from gui.bridge import FutoshikiBridge, InputData, OutputData


# ============================================================================
# ENUMS & TYPES
# ============================================================================

class SolverType(Enum):
    """Available solver algorithms."""
    BACKTRACKING = "backtracking"
    FORWARD_CHAINING = "forward_chaining"
    BACKWARD_CHAINING = "backward_chaining"
    A_STAR = "a_star"


class SolveStatus(Enum):
    """Status of a solve operation."""
    IDLE = "idle"
    SOLVING = "solving"
    SUCCESS = "success"
    UNSOLVABLE = "unsolvable"
    ERROR = "error"
    TIMEOUT = "timeout"


# ============================================================================
# CONTROLLER CLASS
# ============================================================================

class FutoshikiController:
    def __init__(self, update_callback: Callable = None):
        self.bridge = FutoshikiBridge()
        self.update_callback = update_callback or self._default_callback

        # State
        self.current_status = SolveStatus.IDLE
        self.last_result = None
        self.solver_thread = None
        self.is_solving = False
        self.timeout_seconds = 30
        self.stop_event = threading.Event()  # Replaces messy timeout logic

    def _default_callback(self, status: str, data: Dict = None):
        print(f"[Controller] Status: {status}, Data: {data}")

    # ========================================================================
    # PRIMARY EVENT HANDLERS (What GUI calls)
    # ========================================================================

    def handle_solve_request(
        self,
        gui_matrix: List[List[str]],
        gui_constraints: Dict[str, str],
        size: int,
        algorithm: SolverType = SolverType.BACKTRACKING
    ) -> None:
        if self.is_solving:
            self.update_callback('error', {'message': 'Already solving. Please wait.'})
            return

        self.is_solving = True
        self.current_status = SolveStatus.SOLVING
        self.stop_event.clear()  # Reset the stop flag
        self.update_callback('solving', {})

        thread = threading.Thread(
            target=self._solve_worker,
            args=(gui_matrix, gui_constraints, size, algorithm),
            daemon=True
        )
        thread.start()
        self.solver_thread = thread

    def _solve_worker(
        self,
        gui_matrix: List[List[str]],
        gui_constraints: Dict[str, str],
        size: int,
        algorithm: SolverType
    ) -> None:
        try:
            # Step 1: Convert GUI data to solver format
            input_data = self.bridge.ui_to_logic(gui_matrix, gui_constraints, size)

            # Step 2: Call the appropriate solver
            output_data = self._call_solver(input_data, algorithm)

            # Step 3: Convert result back to GUI format
            result_dict = self.bridge.logic_to_ui(output_data)
            self.last_result = result_dict

            # Step 4: Notify UI with result
            if output_data.status == "success":
                self.current_status = SolveStatus.SUCCESS
                self.update_callback('success', result_dict)
            elif output_data.status == "timeout":
                self.current_status = SolveStatus.TIMEOUT
                self.update_callback('error', {'message': 'Solver timed out or was cancelled.'})
            else:
                self.current_status = SolveStatus.UNSOLVABLE
                self.update_callback('unsolvable', result_dict)

        except Exception as e:
            self.current_status = SolveStatus.ERROR
            self.update_callback('error', {
                'message': f'Error during solving: {str(e)}',
                'error_type': type(e).__name__
            })
        finally:
            self.is_solving = False

    def _call_solver(self, input_data: InputData, algorithm: SolverType) -> OutputData:
        """Instantiates and calls the correct solver algorithm."""

        if algorithm == SolverType.BACKTRACKING:
            from src.solvers.backtracking import BacktrackingSolver
            solver = BacktrackingSolver(timeout=self.timeout_seconds)
            return solver.solve(input_data, self.stop_event)

        elif algorithm == SolverType.FORWARD_CHAINING:
            from src.solvers.forward_chaining import ForwardChainingSolver
            solver = ForwardChainingSolver(timeout=self.timeout_seconds)
            return solver.solve(input_data, self.stop_event)

        elif algorithm in [SolverType.A_STAR, SolverType.BACKWARD_CHAINING]:
            # Graceful warning for algorithms not yet wired up
            name = algorithm.name.replace('_', ' ').title()
            return OutputData(
                status='not_implemented',
                solution=input_data.matrix, # Return original grid untouched
                stats={'time_ms': 0},
                message=f"The {name} algorithm is currently out of service. Please select another algorithm."
            )

        return OutputData(status='error', message=f"Unknown solver '{algorithm.value}'.")

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def get_current_status(self) -> str:
        return self.current_status.value

    def get_last_result(self) -> Optional[Dict]:
        return self.last_result

    def cancel_solve(self) -> None:
        """Triggers the stop event to safely cancel the solver."""
        if self.is_solving:
            self.stop_event.set()

    def set_timeout(self, seconds: int) -> None:
        if seconds > 0:
            self.timeout_seconds = seconds

    def load_puzzle_from_file(self, filepath: str) -> Tuple[List[List[str]], Dict[str, str], int]:
        """
        Uses parser.py to load the file, then translates the constraints
        into the specific string keys the GUI requires to display < and > signs.
        """
        from src.utils.parser import load_puzzle_file

        # 1. Parse using your robust parser
        board, initial_state = load_puzzle_file(filepath)

        # 2. Convert Matrix values to GUI strings (empty string for 0)
        gui_matrix = []
        for row in initial_state.board:
            gui_matrix.append([str(val) if val != 0 else "" for val in row])

        # 3. Transform Constraints (r1, c1, op, r2, c2) -> "(r1,c1)-(r2,c2)"
        gui_constraints = {}
        for constraint in board.constraints:
            r1, c1, op, r2, c2 = constraint
            key = f"({r1},{c1})-({r2},{c2})"
            gui_constraints[key] = op

        return gui_matrix, gui_constraints, board.N

    def get_debug_info(self) -> Dict:
        return {
            'status': self.current_status.value,
            'is_solving': self.is_solving,
            'last_result': self.last_result,
            'timeout_seconds': self.timeout_seconds,
            'thread_alive': self.solver_thread.is_alive() if self.solver_thread else False
        }
