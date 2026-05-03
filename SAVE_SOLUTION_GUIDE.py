"""
Usage Guide for save_solution() Function
========================================

The save_solution() function outputs Futoshiki puzzle solutions in a formatted 
layout that displays both the solved numbers and all constraints.

FUNCTION SIGNATURE:
-------------------
def save_solution(board: Tuple[Tuple[int, ...], ...], 
                  constraints: Tuple, 
                  filename: str) -> None

PARAMETERS:
-----------
1. board (Tuple[Tuple[int, ...], ...]):
   - The solved Futoshiki puzzle as a 2D tuple of tuples
   - Example: ((1, 2, 3, 4), (4, 3, 2, 1), (2, 1, 4, 3), (3, 4, 1, 2))
   
2. constraints (Tuple):
   - Tuple of constraint tuples, each formatted as: (r1, c1, operator, r2, c2)
   - operator: '<' or '>'
   - r1, c1: row and column of first cell
   - r2, c2: row and column of second cell
   - Example: ((0, 0, '<', 0, 1), (0, 0, '<', 1, 0), ...)
   
3. filename (str):
   - Output file path (e.g., "outputs/solution.txt")
   - Also prints to stdout

OUTPUT FORMAT:
--------------
The function creates a formatted output with:

1. NUMBER ROWS: Contains solved values with horizontal constraints
   - Format: "number operator number operator number ..."
   - Examples: "1 < 2   3   4" (with and without constraints)
   - Spacing: "number operator number" takes 3 characters

2. CONSTRAINT ROWS: Between number rows, showing vertical constraints
   - "v" indicates cell above is GREATER than cell below (>)
   - "^" indicates cell above is LESS than cell below (<)
   - Spaces indicate no constraint
   - Aligned directly under the numbers they reference

EXAMPLE USAGE:
--------------

from src.utils.parser import load_puzzle_file, save_solution

# Load puzzle
board, state = load_puzzle_file("inputs/4x4_matrix.txt")

# Solve the puzzle (using your solver)
solved_board = solve_puzzle(board, state)

# Save solution
save_solution(solved_board, board.constraints, "outputs/solution.txt")

OUTPUT EXAMPLE (4x4 puzzle):
----------------------------
1 < 2   3   4
^           v
4   3 > 2   1
        ^    
2   1   4   3
^            
3   4 > 1 < 2

Interpretation:
- Row 0: "1 < 2" (1 is less than 2)
- Row 0-1: "^" under 1 means cell (0,0) < cell (1,0)
- Row 0-1: "v" under 4 means cell (0,3) > cell (1,3)
- Row 1: "3 > 2" (3 is greater than 2)
- And so on...

OUTPUT FILE:
------------
Both prints to console AND saves to the specified file with proper formatting.

TIPS:
-----
1. The function handles any board size (4x4, 6x6, 9x9, etc.)
2. Constraints are automatically mapped to either horizontal or vertical
3. Output is always aligned and properly spaced
4. Use with your solver output directly - no transformation needed
"""

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_basic():
    """Basic example: Load, solve, and save."""
    from src.utils.parser import load_puzzle_file, save_solution
    
    # Load puzzle
    board, state = load_puzzle_file("inputs/4x4_matrix.txt")
    
    # Create solved board (replace with actual solver)
    solved_board = (
        (1, 2, 3, 4),
        (4, 3, 2, 1),
        (2, 1, 4, 3),
        (3, 4, 1, 2)
    )
    
    # Save solution with constraints
    save_solution(solved_board, board.constraints, "outputs/my_solution.txt")


def example_with_solver():
    """Example integrating with an actual solver."""
    from src.utils.parser import load_puzzle_file, save_solution
    from src.solvers.backtracking import BacktrackingSolver
    
    # Load puzzle
    board, state = load_puzzle_file("inputs/6x6_matrix.txt")
    
    # Solve using your solver
    solver = BacktrackingSolver()
    solved_state = solver.solve(board, state)
    
    # Save the solution
    if solved_state:
        save_solution(solved_state.board, board.constraints, "outputs/solution_6x6.txt")
    else:
        print("No solution found")


if __name__ == "__main__":
    print(__doc__)
    print("\n" + "=" * 70)
    print("For actual usage, import the function from src.utils.parser")
    print("=" * 70)
