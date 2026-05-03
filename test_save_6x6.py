#!/usr/bin/env python3
"""
Test save_solution with 6x6 puzzle.
"""

from src.utils.parser import load_puzzle_file, save_solution

def test_6x6():
    """Test with a larger 6x6 puzzle."""
    
    input_file = "inputs/6x6_matrix_2.txt"
    output_file = "outputs/test_output_6x6.txt"
    
    try:
        board, state = load_puzzle_file(input_file)
        
        print(f"Testing 6x6 puzzle")
        print(f"Loaded from: {input_file}")
        print(f"Constraints: {len(board.constraints)}\n")
        
        # Create a solved board
        solved_board = (
            (1, 2, 3, 4, 5, 6),
            (6, 5, 4, 3, 2, 1),
            (2, 3, 1, 6, 4, 5),
            (5, 4, 6, 2, 1, 3),
            (3, 6, 2, 1, 5, 4),
            (4, 1, 5, 3, 6, 2)
        )
        
        print("Saving to file...")
        save_solution(solved_board, board.constraints, output_file)
        print(f"✓ Solution saved to {output_file}\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_6x6()
