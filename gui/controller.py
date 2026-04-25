"""
Controller Module: GUI ↔ Solver Communication Hub
===================================================
This module mediates between the tkinter GUI and the solver algorithms.

Design Pattern: MVC (Model-View-Controller)
- Model: Board state (in src/models/)
- View: tkinter GUI components
- Controller: This file - handles events and coordinates data flow

Flow:
1. User clicks "Solve" button → GUI calls controller.handle_solve_request()
2. Controller converts GUI data via Bridge
3. Controller calls appropriate solver from src/solvers/
4. Controller passes result back to GUI for rendering
5. GUI updates display
"""

import asyncio
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
    """
    Main controller for orchestrating solve requests.
    
    Responsibilities:
    1. Listen for UI events (buttons, file selection)
    2. Validate input data
    3. Call appropriate solver algorithm
    4. Handle async execution (non-blocking UI)
    5. Pass results back to GUI for rendering
    """

    def __init__(self, update_callback: Callable = None):
        """
        Initialize the controller.
        
        Args:
            update_callback: Function to call when state changes.
                           Signature: update_callback(status, data)
        """
        self.bridge = FutoshikiBridge()
        self.update_callback = update_callback or self._default_callback
        
        # State
        self.current_status = SolveStatus.IDLE
        self.last_result = None
        self.solver_thread = None
        self.is_solving = False
        self.timeout_seconds = 30

    def _default_callback(self, status: str, data: Dict = None):
        """Default callback if none provided."""
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
        """
        Handle a "Solve" button click from the GUI.
        Runs in a background thread to keep UI responsive.
        
        Args:
            gui_matrix: 2D list of cell values from GUI (strings)
            gui_constraints: Dict of constraints from GUI
            size: Grid size (4-9)
            algorithm: Which solver to use
        
        Callback Flow:
        1. Calls update_callback('solving', {})
        2. ... (solver runs) ...
        3. Calls update_callback('success'/'error', result)
        
        TODO: Algorithm Team
        - Implement solver selection logic
        - Map SolverType enum to actual solver imports from src/solvers/
        - Handle solver timeouts gracefully
        """
        # Prevent multiple simultaneous solve requests
        if self.is_solving:
            self.update_callback('error', {
                'message': 'Already solving. Please wait.'
            })
            return

        # Start solving in background thread
        self.is_solving = True
        self.current_status = SolveStatus.SOLVING
        self.update_callback('solving', {})

        # Run in thread
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
        """
        Background thread worker that performs the actual solve.
        Never call this directly - use handle_solve_request().
        """
        try:
            # Step 1: Convert GUI data to solver format
            input_data = self.bridge.ui_to_logic(
                gui_matrix, gui_constraints, size
            )

            # Step 2: Call the appropriate solver
            # TODO: ALGORITHM TEAM - IMPLEMENT THIS
            # The solver should:
            # - Accept InputData
            # - Return OutputData
            # - Respect self.timeout_seconds
            
            output_data = self._call_solver(input_data, algorithm)

            # Step 3: Convert result back to GUI format
            result_dict = self.bridge.logic_to_ui(output_data)
            self.last_result = result_dict

            # Step 4: Notify UI with result
            if output_data.status == "success":
                self.current_status = SolveStatus.SUCCESS
                self.update_callback('success', result_dict)
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

    def _call_solver(
        self,
        input_data: InputData,
        algorithm: SolverType
    ) -> OutputData:
        """Call the appropriate solver algorithm and return OutputData."""
        import time
        from src.models.state import State
        from src.models.board import Board

        # Build immutable State and Board from InputData
        matrix_tuple = tuple(tuple(row) for row in input_data.matrix)
        initial_state = State(matrix_tuple, None)

        # Convert constraints from ((r1,c1),(r2,c2),sign) → (r1,c1,sign,r2,c2)
        constraints = tuple(
            (c1[0], c1[1], sign, c2[0], c2[1])
            for c1, c2, sign in input_data.constraints
        )
        board = Board(input_data.size, initial_state, constraints)

        start = time.time()

        if algorithm == SolverType.BACKTRACKING:
            from src.solvers.backtracking import BacktrackingSolver
            solver = BacktrackingSolver()
            solution_grid = solver.solve(board)
            elapsed = solver.solve_time
            stats = {
                'Algorithm': 'Backtracking',
                'Time': f'{elapsed:.4f}s',
                'Nodes visited': solver.nodes_visited,
            }
            solution = [list(row) for row in solution_grid] if solution_grid else None

        elif algorithm == SolverType.FORWARD_CHAINING:
            from src.solvers.forward_chaining import forward_chaining_solver
            from src.models.kb import KnowledgeBase
            from src.logic.grounding import ground_axioms
            kb = KnowledgeBase(board.N)
            ground_axioms(kb, board)
            solution_state = forward_chaining_solver(initial_state, kb)
            elapsed = time.time() - start
            is_complete = solution_state is not None and solution_state.is_complete()
            stats = {
                'Algorithm': 'Forward Chaining',
                'Time': f'{elapsed:.4f}s',
                'Clauses grounded': len(kb.clauses),
                'Result': 'Complete' if is_complete else ('Partial (unit prop only)' if solution_state else 'Contradiction'),
            }
            # Show partial result on board; only block on hard contradiction (None)
            solution = [list(row) for row in solution_state.board] if solution_state else None

        elif algorithm == SolverType.A_STAR:
            from src.solvers.a_star import a_star_solver
            solution_state = a_star_solver(initial_state, board, "advanced")
            elapsed = time.time() - start
            stats = {
                'Algorithm': 'A*',
                'Time': f'{elapsed:.4f}s',
            }
            complete = solution_state and solution_state.is_complete()
            solution = [list(row) for row in solution_state.board] if complete else None

        else:
            return OutputData(
                status='error',
                stats={},
                message=f'Solver "{algorithm.value}" is not implemented.'
            )

        if solution is not None:
            return OutputData(status='success', solution=solution, stats=stats, message='Solved!')
        return OutputData(status='unsolvable', solution=None, stats=stats, message='No solution found.')

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def get_current_status(self) -> str:
        """Get current solve status as string."""
        return self.current_status.value

    def get_last_result(self) -> Optional[Dict]:
        """Get the last solve result."""
        return self.last_result

    def cancel_solve(self) -> None:
        """Cancel the current solve operation (if possible)."""
        # Note: Canceling a thread is tricky in Python
        # For now, we just set a flag
        self.is_solving = False
        self.current_status = SolveStatus.IDLE

    def set_timeout(self, seconds: int) -> None:
        """Set solver timeout in seconds."""
        if seconds > 0:
            self.timeout_seconds = seconds

    def load_puzzle_from_file(self, filepath: str) -> Tuple[List[List[str]], Dict[str, str], int]:
        """
        Load puzzle from a .txt file.
        
        Args:
            filepath: Path to puzzle file
        
        Returns:
            (gui_matrix, gui_constraints, size)
        
        TODO: Implement file parsing
        - Use src/utils/parser.py to read the file
        - Return data in GUI format
        """
        # PLACEHOLDER
        return [], {}, 4

    # ========================================================================
    # DEBUG & MONITORING
    # ========================================================================

    def get_debug_info(self) -> Dict:
        """Get debug information about current state."""
        return {
            'status': self.current_status.value,
            'is_solving': self.is_solving,
            'last_result': self.last_result,
            'timeout_seconds': self.timeout_seconds,
            'thread_alive': self.solver_thread.is_alive() if self.solver_thread else False
        }
