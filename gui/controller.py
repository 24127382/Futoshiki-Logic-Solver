"""
Controller Module: GUI ↔ Solver Communication Hub
"""
import threading
from typing import Dict, List, Callable, Optional, Tuple
from enum import Enum
import sys
from pathlib import Path

src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from gui.bridge import FutoshikiBridge, InputData, OutputData

class SolverType(Enum):
    BACKTRACKING = "backtracking"
    FORWARD_CHAINING = "forward_chaining"
    BACKWARD_CHAINING = "backward_chaining"
    A_STAR = "a_star"

class SolveStatus(Enum):
    IDLE = "idle"
    SOLVING = "solving"
    SUCCESS = "success"
    UNSOLVABLE = "unsolvable"
    ERROR = "error"
    TIMEOUT = "timeout"

class FutoshikiController:
    def __init__(self, update_callback: Callable = None):
        self.bridge = FutoshikiBridge()
        self.update_callback = update_callback or self._default_callback
        self.current_status = SolveStatus.IDLE
        self.last_result = None
        self.solver_thread = None
        self.is_solving = False
        self.timeout_seconds = 30
        self.stop_event = threading.Event()
        self.timeout_timer = None  # Timer to force timeout

    def _default_callback(self, status: str, data: Dict = None):
        pass

    def handle_solve_request(
        self, gui_matrix: List[List[str]], gui_constraints: Dict[str, str], size: int, algorithm: SolverType
    ) -> None:
        if self.is_solving:
            self.update_callback('error', {'message': 'Already solving. Please wait.'})
            return

        self.is_solving = True
        self.current_status = SolveStatus.SOLVING
        self.stop_event.clear()
        self.update_callback('solving', {})

        # 1. Start the solver thread
        thread = threading.Thread(
            target=self._solve_worker,
            args=(gui_matrix, gui_constraints, size, algorithm),
            daemon=True
        )
        thread.start()
        self.solver_thread = thread

        # 2. Start the hard timeout timer
        if self.timeout_timer:
            self.timeout_timer.cancel()
        self.timeout_timer = threading.Timer(self.timeout_seconds, self._force_timeout)
        self.timeout_timer.start()

    def _force_timeout(self) -> None:
        """Called automatically if the timer expires."""
        if self.is_solving:
            self.stop_event.set() # Attempt to gracefully stop solver
            self.is_solving = False
            self.current_status = SolveStatus.TIMEOUT
            self.update_callback('error', {'message': f'Time limit of {self.timeout_seconds}s exceeded! Solver stopped.'})

    def _solve_worker(self, gui_matrix: List[List[str]], gui_constraints: Dict[str, str], size: int, algorithm: SolverType) -> None:
        try:
            input_data = self.bridge.ui_to_logic(gui_matrix, gui_constraints, size)
            output_data = self._call_solver(input_data, algorithm)

            # If _force_timeout already fired, ignore the late result
            if not self.is_solving: return

            # Cancel timer if we finished successfully before timeout
            if self.timeout_timer: self.timeout_timer.cancel()

            result_dict = self.bridge.logic_to_ui(output_data)
            self.last_result = result_dict

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
            if not self.is_solving: return
            if self.timeout_timer: self.timeout_timer.cancel()
            self.current_status = SolveStatus.ERROR
            self.update_callback('error', {'message': f'Error during solving: {str(e)}'})
        finally:
            self.is_solving = False

    def _call_solver(self, input_data: InputData, algorithm: SolverType) -> OutputData:
        """
        Dynamically attempts to load the selected solver.
        If the file or class does not exist yet, it catches the error and warns the user.
        """
        try:
            if algorithm == SolverType.BACKTRACKING:
                from src.solvers.backtracking import BacktrackingSolver as TargetSolver
            elif algorithm == SolverType.FORWARD_CHAINING:
                from src.solvers.forward_chaining import ForwardChainingSolver as TargetSolver
            elif algorithm == SolverType.BACKWARD_CHAINING:
                from src.solvers.backward_chaining import BackwardChainingSolver as TargetSolver
            elif algorithm == SolverType.A_STAR:
                from src.solvers.a_star import A_StarSolver as TargetSolver
            else:
                return OutputData(status='error', message=f"Unknown solver '{algorithm.value}'.")

            # If the import succeeds, instantiate and run!
            solver = TargetSolver(timeout=self.timeout_seconds)
            return solver.solve(input_data, self.stop_event)

        except (ImportError, ModuleNotFoundError):
            # This triggers if the file (e.g., backward_chaining.py) isn't made yet
            name = algorithm.name.replace('_', ' ').title()
            return OutputData(
                status='not_implemented',
                solution=input_data.matrix,
                stats={'time_ms': 0},
                message=f"The {name} algorithm is not in service yet.\n(Source code missing or incomplete)"
            )

    def cancel_solve(self) -> None:
        if self.is_solving:
            self.stop_event.set()
            if self.timeout_timer: self.timeout_timer.cancel()

    def set_timeout(self, seconds: int) -> None:
        if seconds > 0: self.timeout_seconds = seconds

    def load_puzzle_from_file(self, filepath: str) -> Tuple[List[List[str]], Dict[str, str], int]:
        from src.utils.parser import load_puzzle_file
        board, initial_state = load_puzzle_file(filepath)
        gui_matrix = [[str(val) if val != 0 else "" for val in row] for row in initial_state.board]
        gui_constraints = {f"({r1},{c1})-({r2},{c2})": op for r1, c1, op, r2, c2 in board.constraints}
        return gui_matrix, gui_constraints, board.N
