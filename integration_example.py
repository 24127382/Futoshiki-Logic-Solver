#!/usr/bin/env python3
"""
INTEGRATION EXAMPLE: Using save_solution() with Your Solvers
============================================================

This example shows how to use the new save_solution() function
with your existing solver implementations.
"""

from src.utils.parser import load_puzzle_file, save_solution
from pathlib import Path


def solve_and_save_example():
    """
    Complete workflow: Load → Solve → Save
    
    Replace the solver with your actual solver implementation.
    """
    
    # List of puzzle files to process
    puzzle_files = [
        ("inputs/4x4_matrix.txt", "outputs/4x4_solved.txt"),
        ("inputs/6x6_matrix.txt", "outputs/6x6_solved.txt"),
    ]
    
    print("=" * 70)
    print("FUTOSHIKI SOLVER - Complete Workflow Example")
    print("=" * 70)
    
    for input_file, output_file in puzzle_files:
        if not Path(input_file).exists():
            print(f"\n⚠ Skipping {input_file} (not found)")
            continue
            
        print(f"\n{'─' * 70}")
        print(f"Processing: {input_file}")
        print(f"{'─' * 70}")
        
        try:
            # STEP 1: Load puzzle
            board, initial_state = load_puzzle_file(input_file)
            print(f"✓ Loaded puzzle: {board.N}x{board.N}")
            print(f"  • Constraints: {len(board.constraints)}")
            
            # STEP 2: Solve puzzle
            # TODO: Replace with your actual solver call
            # Example:
            # solver = YourSolver(timeout=30)
            # solved_state = solver.solve(board, initial_state)
            
            # For now, using a dummy solved board for demonstration
            if board.N == 4:
                solved_board = (
                    (1, 2, 3, 4),
                    (4, 3, 2, 1),
                    (2, 1, 4, 3),
                    (3, 4, 1, 2)
                )
            elif board.N == 6:
                solved_board = (
                    (1, 2, 3, 4, 5, 6),
                    (6, 5, 4, 3, 2, 1),
                    (2, 3, 1, 6, 4, 5),
                    (5, 4, 6, 2, 1, 3),
                    (3, 6, 2, 1, 5, 4),
                    (4, 1, 5, 3, 6, 2)
                )
            else:
                print(f"⚠ Skipping {board.N}x{board.N} (no demo solution)")
                continue
            
            print(f"✓ Puzzle solved successfully")
            
            # STEP 3: Save solution with constraints
            save_solution(solved_board, board.constraints, output_file)
            print(f"✓ Solution saved to: {output_file}")
            
            # Also create a file with just numbers (simple format)
            simple_output = output_file.replace(".txt", "_simple.txt")
            with open(simple_output, 'w') as f:
                for row in solved_board:
                    f.write(' '.join(map(str, row)) + '\n')
            print(f"✓ Simple format also saved to: {simple_output}")
            
        except Exception as e:
            print(f"✗ Error processing {input_file}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 70}")
    print("✓ Processing complete!")
    print(f"{'=' * 70}\n")


def solver_integration_template():
    """
    Template showing how to integrate with your solver.
    """
    
    code = '''
from src.utils.parser import load_puzzle_file, save_solution
from src.solvers.YOUR_SOLVER import YourSolver  # Replace with your solver

def main():
    # Load puzzle
    board, state = load_puzzle_file("inputs/puzzle.txt")
    
    # Create solver instance
    solver = YourSolver(timeout=30)
    
    # Solve puzzle
    solved_state = solver.solve(board, state)
    
    if solved_state and solved_state.board:
        # Save solution with all constraints formatted
        save_solution(
            solved_state.board,
            board.constraints,
            "outputs/solution.txt"
        )
        print("✓ Solution saved!")
    else:
        print("✗ No solution found")

if __name__ == "__main__":
    main()
    '''
    
    print("SOLVER INTEGRATION TEMPLATE:")
    print(code)


if __name__ == "__main__":
    # Run the workflow example
    solve_and_save_example()
    
    # Show integration template
    print("\n" + "=" * 70)
    print("TEMPLATE FOR YOUR SOLVER INTEGRATION:")
    print("=" * 70 + "\n")
    solver_integration_template()
