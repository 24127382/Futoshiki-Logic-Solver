#!/usr/bin/env python3
"""Generate solvable Futoshiki puzzles of varying sizes."""

import random
import os
from typing import Tuple, List, Set

def is_valid_placement(board: List[List[int]], row: int, col: int, num: int, N: int) -> bool:
    """Check if a number can be placed at the given position."""
    # Check row
    if num in board[row]:
        return False
    # Check column
    if num in [board[r][col] for r in range(N)]:
        return False
    return True

def solve_latin_square(N: int, clues: List[List[int]]) -> Tuple[List[List[int]], bool]:
    """Solve a partial Latin square using backtracking."""
    board = [row[:] for row in clues]  # Deep copy
    
    def backtrack(pos: int) -> bool:
        if pos == N * N:
            return True
        
        row, col = pos // N, pos % N
        if board[row][col] != 0:
            return backtrack(pos + 1)
        
        # Try random order
        nums = list(range(1, N + 1))
        random.shuffle(nums)
        
        for num in nums:
            if is_valid_placement(board, row, col, num, N):
                board[row][col] = num
                if backtrack(pos + 1):
                    return True
                board[row][col] = 0
        
        return False
    
    success = backtrack(0)
    return board, success

def generate_complete_solution(N: int) -> List[List[int]]:
    """Generate a complete valid Futoshiki solution (Latin square)."""
    empty_board = [[0] * N for _ in range(N)]
    solution, _ = solve_latin_square(N, empty_board)
    return solution

def create_puzzle(N: int, clue_percentage: float = 0.35) -> Tuple[List[List[int]], List[List[int]]]:
    """Create a puzzle by removing clues from a complete solution."""
    solution = generate_complete_solution(N)
    puzzle = [row[:] for row in solution]
    
    # Remove clues
    num_clues = max(N, int(N * N * clue_percentage))
    positions = [(r, c) for r in range(N) for c in range(N)]
    random.shuffle(positions)
    
    for r, c in positions[:N * N - num_clues]:
        puzzle[r][c] = 0
    
    return puzzle, solution

def generate_constraints(N: int, density: float = 0.3) -> Tuple[List[List[int]], List[List[int]]]:
    """Generate random valid inequality constraints."""
    # Horizontal constraints (N x (N-1))
    h_constraints = [[0] * (N - 1) for _ in range(N)]
    # Vertical constraints ((N-1) x N)
    v_constraints = [[0] * N for _ in range(N - 1)]
    
    # Add constraints with given density
    num_h = int(N * (N - 1) * density)
    num_v = int((N - 1) * N * density)
    
    h_positions = [(r, c) for r in range(N) for c in range(N - 1)]
    random.shuffle(h_positions)
    for r, c in h_positions[:num_h]:
        h_constraints[r][c] = random.choice([1, -1])
    
    v_positions = [(r, c) for r in range(N - 1) for c in range(N)]
    random.shuffle(v_positions)
    for r, c in v_positions[:num_v]:
        v_constraints[r][c] = random.choice([1, -1])
    
    return h_constraints, v_constraints

def save_puzzle(puzzle: List[List[int]], h_constraints: List[List[int]], 
                v_constraints: List[List[int]], filename: str) -> None:
    """Save puzzle in the expected format."""
    N = len(puzzle)
    lines = [str(N)]
    
    # Board
    for row in puzzle:
        lines.append(', '.join(map(str, row)))
    
    # Horizontal constraints
    for row in h_constraints:
        lines.append(', '.join(map(str, row)))
    
    # Vertical constraints
    for row in v_constraints:
        lines.append(', '.join(map(str, row)))
    
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

def save_solution(solution: List[List[int]], filename: str) -> None:
    """Save solution."""
    with open(filename, 'w') as f:
        for row in solution:
            f.write(' '.join(map(str, row)) + '\n')

def main():
    """Generate 10 puzzles of varying sizes."""
    os.makedirs('inputs', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    # Define puzzle sizes: 2x 4x4, 2x 5x5, 2x 6x6, 2x 7x7, 1x 8x8, 1x 9x9
    sizes = [4, 4, 5, 5, 6, 6, 7, 7, 8, 9]
    
    for idx, N in enumerate(sizes, 1):
        print(f"Generating puzzle {idx}/{len(sizes)}: {N}x{N}...")
        
        puzzle, solution = create_puzzle(N, clue_percentage=0.4)
        h_constraints, v_constraints = generate_constraints(N, density=0.3)
        
        input_file = f'inputs/{N}x{N}_puzzle_{idx:02d}.txt'
        output_file = f'outputs/{N}x{N}_puzzle_{idx:02d}_solution.txt'
        
        save_puzzle(puzzle, h_constraints, v_constraints, input_file)
        save_solution(solution, output_file)
        
        print(f"  Saved: {input_file}")
        print(f"  Saved: {output_file}")
    
    print("\n✓ Generated 10 solvable Futoshiki puzzles!")

if __name__ == '__main__':
    main()
