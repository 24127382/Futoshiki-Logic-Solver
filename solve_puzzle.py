#!/usr/bin/env python3
"""
Script to solve a Futoshiki puzzle from input file.
Usage: python solve_puzzle.py <input_file>
"""

import sys
from src.models.board import Board
from src.models.kb import KnowledgeBase
from src.models.state import State
from src.solvers.forward_chaining import forward_chaining_solver
from src.logic.grounding import ground_axioms


def load_puzzle(filename):
    """Load puzzle from file format:
    Line 1: N (board size)
    Lines 2 to N+1: Initial board state (N values per line, 0 = empty)
    Last line: Constraints (format: row col op row col op ...)
    """
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    N = int(lines[0].strip())
    
    # Load initial state
    initial_board = []
    for i in range(1, N + 1):
        row = tuple(map(int, lines[i].split()))
        initial_board.append(row)
    initial_board = tuple(initial_board)
    
    # Parse constraints (simplified format)
    constraints = []
    if len(lines) > N + 1:
        constraint_line = lines[N + 1].strip()
        parts = constraint_line.split()
        for i in range(0, len(parts), 3):
            if i + 2 < len(parts):
                parts_list = parts[i:i+3]
                r, c, op = int(parts_list[0]), int(parts_list[1]), parts_list[2]
                constraints.append((r, c, op))
    
    return N, initial_board, tuple(constraints)


def print_board(board, title="Board"):
    """Pretty print a board."""
    print(f"\n{title}:")
    print("+" + "-"*3 + "+" * len(board[0]))
    for row in board:
        print("|" + "|".join(str(x) if x != 0 else " " for x in row) + "|")
    print("+" + "-"*3 + "+" * len(board[0]))


def solve_puzzle(input_file):
    """Load and solve a puzzle."""
    print(f"Loading puzzle from {input_file}...")
    
    try:
        N, initial_board, constraints = load_puzzle(input_file)
    except Exception as e:
        print(f"Error loading puzzle: {e}")
        return
    
    print(f"Board size: {N}x{N}")
    print(f"Constraints: {len(constraints)}")
    
    # Create board and knowledge base
    initial_state = State(initial_board, None)
    print_board(initial_board, "Initial State")
    
    board = Board(N, initial_state, constraints)
    kb = KnowledgeBase(N)
    
    # Ground all axioms
    print("\nGrounding axioms...")
    ground_axioms(kb, board)
    print(f"Generated {len(kb.clauses)} clauses")
    
    # Solve using forward chaining
    print("\nSolving with Forward Chaining...")
    solution = forward_chaining_solver(initial_state, kb)
    
    if solution:
        print_board(solution.board, "Solution")
        print("\n✓ Puzzle solved!")
    else:
        print("\n✗ No solution found")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python solve_puzzle.py <input_file>")
        print("Example: python solve_puzzle.py inputs/puzzle_3x3_simple.txt")
        sys.exit(1)
    
    solve_puzzle(sys.argv[1])
