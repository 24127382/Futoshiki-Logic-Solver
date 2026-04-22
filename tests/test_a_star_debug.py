"""Debug A* solver to check why it's not finding solutions."""

import sys
from pathlib import Path

src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.utils.parser import load_puzzle_file
from src.solvers.a_star import a_star_solver

# Load puzzle
board, initial_state = load_puzzle_file("inputs/4x4_matrix.txt")

print("Board size:", board.N)
print("Initial state board:", initial_state.board)
print("Number of constraints:", len(board.constraints))
print("Constraints:", board.constraints)
print()

# Try to solve
print("Attempting A* solve...")
solution = a_star_solver(initial_state, board, "advanced")

if solution:
    print("Solution found!")
    print(solution.board)
else:
    print("No solution found")
    
    # Debug: Check if initial state is valid
    from src.solvers.a_star import _is_partial_valid, _filled_cells
    print("\nDebug info:")
    print(f"  Initial state valid: {_is_partial_valid(initial_state.board, board)}")
    print(f"  Filled cells: {_filled_cells(initial_state.board)}")
