#!/usr/bin/env python3
"""
Test script for the save_solution function.
Demonstrates the output format with constraints.
"""

from src.utils.parser import load_puzzle_file, save_solution

def test_save_solution():
    """Test the save_solution function with a sample puzzle."""
    
    # Load a puzzle
    print("=" * 60)
    print("Testing save_solution function")
    print("=" * 60)
    
    # Test with 4x4 puzzle
    input_file = "inputs/4x4_matrix.txt"
    output_file = "outputs/test_output_4x4.txt"
    
    try:
        board, state = load_puzzle_file(input_file)
        
        print(f"\nLoaded puzzle from: {input_file}")
        print(f"Board size: {board.N}x{board.N}")
        print(f"Number of constraints: {len(board.constraints)}")
        
        # Create a solved board (for testing purposes)
        solved_board = (
            (1, 2, 3, 4),
            (4, 3, 2, 1),
            (2, 1, 4, 3),
            (3, 4, 1, 2)
        )
        
        print(f"\nSolved board:")
        for row in solved_board:
            print(row)
        
        print(f"\nConstraints:")
        for i, constraint in enumerate(board.constraints):
            r1, c1, op, r2, c2 = constraint
            print(f"  {i+1}. ({r1},{c1}) {op} ({r2},{c2})")
        
        print(f"\nSaving solution to: {output_file}")
        save_solution(solved_board, board.constraints, output_file)
        print(f"✓ Solution saved successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_save_solution()
