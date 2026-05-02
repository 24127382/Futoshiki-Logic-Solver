import time
from typing import Tuple, List, Optional, Any

class BacktrackingSolver:
    """
    Standard backtracking solver for Futoshiki puzzles.
    """

    def __init__(self):
        self.nodes_visited = 0
        self.solve_time = 0.0

    def solve(self, board: Any) -> Optional[Tuple[Tuple[int, ...], ...]]:
        self.nodes_visited = 0
        start_time = time.time()

        # Convert immutable tuple grid to a mutable list of lists
        working_grid = [list(row) for row in board.initial_state.board]

        # Run standard backtracking
        if self._backtrack(working_grid, board.N, board.constraints):
            self.solve_time = time.time() - start_time
            # Return as tuple of tuples for output formatting
            return tuple(tuple(row) for row in working_grid)

        self.solve_time = time.time() - start_time
        return None

    def _backtrack(self, grid: List[List[int]], N: int, constraints: Tuple) -> bool:
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

                if self._backtrack(grid, N, constraints):
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
        if val in grid[r]:
            return False

        # Check Column
        for i in range(N):
            if grid[i][c] == val:
                return False

        # Check Inequalities
        grid[r][c] = val
        valid = self._check_inequalities(grid, constraints, r, c)
        grid[r][c] = 0

        return valid

    def _check_inequalities(self, grid: List[List[int]], constraints: Tuple, current_r: int, current_c: int) -> bool:
        """
        Evaluates horizontal and vertical inequalities.
        Constraints are expected in (r1, c1, op, r2, c2) format.
        """
        for constraint in constraints:
            r1, c1, op, r2, c2 = constraint

            # Only test if our current placement touches this rule
            if (current_r == r1 and current_c == c1) or (current_r == r2 and current_c == c2):
                val1 = grid[r1][c1]
                val2 = grid[r2][c2]

                # Enforce rule only when BOTH cells have numbers
                if val1 != 0 and val2 != 0:
                    if op == '<' and not (val1 < val2): return False
                    if op == '>' and not (val1 > val2): return False

        return True
