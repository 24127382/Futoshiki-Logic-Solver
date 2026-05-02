#!/usr/bin/env python3
"""
Script to solve a Futoshiki puzzle from input file.
Usage: python solve_puzzle.py <input_file>

Uses optimized solver with:
- Clause indexing by length for O(1) unit clause lookup
- Partial grounding to skip pre-filled cells
- Active clause tracking in forward chaining
- Pre-computed variable mapping for solution reconstruction
"""

import sys
from src.models.board import Board
from src.models.kb import KnowledgeBase
from src.models.state import State
from src.solvers.forward_chaining import forward_chaining_solver
from src.logic.grounding import ground_axioms
from src.utils.parser import load_puzzle_file, format_board


def solve_puzzle(input_file: str) -> None:
    """Load and solve a puzzle."""
    print(f"Loading puzzle from {input_file}...")
    
    try:
        board, initial_state = load_puzzle_file(input_file)
    except Exception as e:
        print(f"Error loading puzzle: {e}")
        return
    
    N = board.N
    print(f"Board size: {N}x{N}")
    print(f"Constraints: {len(board.constraints)}")
    print(format_board(initial_state.board, "Initial State"))
    
    # Create knowledge base
    kb = KnowledgeBase(N)
    
    # Ground all axioms (with optimizations)
    print("\nGrounding axioms...")
    ground_axioms(kb, board)
    print(f"Generated {len(kb.clauses)} clauses")
    print(f"  Length distribution: {kb.clauses_by_length}")
    
    # Solve using forward chaining (with optimizations)
    print("\nSolving with Forward Chaining...")
    solution = forward_chaining_solver(initial_state, kb)
    
    if solution:
        print(format_board(solution.board, "Solution"))
        print("\n✓ Puzzle solved!")
    else:
        print("\n✗ No solution found")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python solve_puzzle.py <input_file>")
        print("Example: python solve_puzzle.py inputs/puzzle_3x3_simple.txt")
        sys.exit(1)
    
    solve_puzzle(sys.argv[1])
