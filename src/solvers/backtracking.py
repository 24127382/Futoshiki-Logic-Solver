import time
from typing import Tuple, List, Optional, Any
import threading

from gui.bridge import InputData, OutputData

class BacktrackingSolver:
    """
    Standard backtracking solver adapted for the GUI.
    """

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.nodes_visited = 0
        self.start_time = 0.0

    def solve(self, input_data: InputData, stop_event: threading.Event = None) -> OutputData:
        self.nodes_visited = 0
        self.start_time = time.time()

        N = input_data.size
        # Convert GUI matrix to mutable list of lists
        working_grid = [list(row) for row in input_data.matrix]

        # Convert GUI constraints: ((r1, c1), (r2, c2), op) -> (r1, c1, op, r2, c2)
        constraints = []
        for (r1, c1), (r2, c2), op in input_data.constraints:
            constraints.append((r1, c1, op, r2, c2))
        constraints_tuple = tuple(constraints)

        # Run standard backtracking
        success = self._backtrack(working_grid, N, constraints_tuple, stop_event)

        solve_time_ms = (time.time() - self.start_time) * 1000

        # Handle cancellation/timeout
        if stop_event and stop_event.is_set():
            return OutputData(
                status='timeout',
                solution=None,
                stats={'time_ms': round(solve_time_ms, 2), 'nodes_visited': self.nodes_visited},
                message="Solver timed out or was cancelled."
            )

        # Handle normal completion
        status = 'success' if success else 'unsolvable'
        message = 'Puzzle solved successfully' if success else 'No solution exists.'

        return OutputData(
            status=status,
            solution=working_grid if success else None,
            stats={
                'time_ms': round(solve_time_ms, 2),
                'nodes_visited': self.nodes_visited,
                'algorithm': 'Backtracking'
            },
            message=message
        )

    def _backtrack(self, grid: List[List[int]], N: int, constraints: Tuple, stop_event: threading.Event) -> bool:
        # Periodic check for cancellation to keep the algorithm fast but responsive
        if self.nodes_visited % 1000 == 0 and stop_event and stop_event.is_set():
            return False

        self.nodes_visited += 1

        # Find next empty cell
        cell = self._select_unassigned_variable(grid, N)
        if not cell:
            return True  # Puzzle solved

        r, c = cell

        # Try values 1 through N
        for val in range(1, N + 1):
            if self._is_valid(grid, N, constraints, r, c, val):
                grid[r][c] = val

                if self._backtrack(grid, N, constraints, stop_event):
                    return True

                grid[r][c] = 0 # Undo

        return False

    def _select_unassigned_variable(self, grid: List[List[int]], N: int) -> Optional[Tuple[int, int]]:
        for r in range(N):
            for c in range(N):
                if grid[r][c] == 0:
                    return (r, c)
        return None

    def _is_valid(self, grid: List[List[int]], N: int, constraints: Tuple, r: int, c: int, val: int) -> bool:
        # Check Row
        if val in grid[r]: return False
        # Check Column
        for i in range(N):
            if grid[i][c] == val: return False

        # Check Inequalities
        grid[r][c] = val
        valid = self._check_inequalities(grid, constraints, r, c)
        grid[r][c] = 0

        return valid

    def _check_inequalities(self, grid: List[List[int]], constraints: Tuple, current_r: int, current_c: int) -> bool:
        for constraint in constraints:
            r1, c1, op, r2, c2 = constraint
            if (current_r == r1 and current_c == c1) or (current_r == r2 and current_c == c2):
                val1 = grid[r1][c1]
                val2 = grid[r2][c2]
                if val1 != 0 and val2 != 0:
                    if op == '<' and not (val1 < val2): return False
                    if op == '>' and not (val1 > val2): return False
        return True
