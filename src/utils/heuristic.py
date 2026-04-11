"""Heuristic functions for informed search algorithms (A*, greedy best-first, etc.)

Provides various heuristics for estimating remaining effort in puzzle solving.
"""

from typing import Tuple
from src.models.state import State
from src.models.board import Board


def h_remaining_cells(state: State) -> int:
    """Simple heuristic: count remaining empty cells.
    
    h(s) = number of cells with value 0
    
    Admissible: Yes (each cell needs at least 1 assignment)
    
    Args:
        state: Current puzzle state
        
    Returns:
        Number of empty cells
    """
    return sum(1 for row in state.board for cell in row if cell == 0)


def h_constraint_violations(state: State, board: Board) -> int:
    """Count constraint violations in current state.
    
    h(s) = sum of violated row uniqueness + column uniqueness + inequalities
    
    Heuristic: penalizes states with duplicate values in rows/columns
    
    Args:
        state: Current puzzle state
        board: The puzzle board with constraints
        
    Returns:
        Number of detected violations
    """
    violations = 0
    N = len(state.board)
    
    # Check row uniqueness violations
    for row in state.board:
        filled = [val for val in row if val != 0]
        if len(filled) != len(set(filled)):
            violations += len(filled) - len(set(filled))
    
    # Check column uniqueness violations
    for c in range(N):
        col = [state.board[r][c] for r in range(N)]
        filled = [val for val in col if val != 0]
        if len(filled) != len(set(filled)):
            violations += len(filled) - len(set(filled))
    
    return violations


def h_missing_values(state: State) -> int:
    """Count missing values that must be placed.
    
    h(s) = sum of missing values per row + missing values per column
    
    Better than h_remaining_cells for partially filled boards
    
    Args:
        state: Current puzzle state
        
    Returns:
        Count of missing placements needed
    """
    N = len(state.board)
    missing = 0
    
    # Count missing values per row
    for row in state.board:
        filled = set(val for val in row if val != 0)
        missing += len(set(range(1, N + 1)) - filled)
    
    # Count missing values per column (avoid double counting)
    for c in range(N):
        col = [state.board[r][c] for r in range(N)]
        filled = set(val for val in col if val != 0)
        missing += len(set(range(1, N + 1)) - filled)
    
    return missing // 2  # Avoid double counting


def h_most_constrained_value(state: State) -> int:
    """Heuristic based on most-constrained-variable (MCV) principle.
    
    Returns count of cells with minimum possible values.
    Useful for variable ordering in backtracking.
    
    Args:
        state: Current puzzle state
        
    Returns:
        Number of cells with only 1 possible value
    """
    N = len(state.board)
    constrained = 0
    
    for r in range(N):
        for c in range(N):
            if state.board[r][c] == 0:  # Empty cell
                # Count how many values are already used in row/col
                used = set()
                used.update(state.board[r])  # Row
                used.update(state.board[rr][c] for rr in range(N))  # Column
                used.discard(0)
                
                remaining = N - len(used)
                if remaining == 1:
                    constrained += 1
    
    return constrained


def h_sum_remaining_values(state: State) -> int:
    """Sum of possible values for each empty cell.
    
    h(s) = sum over all empty cells of (N - values already used in row/col)
    
    Better differentiation than h_remaining_cells
    
    Args:
        state: Current puzzle state
        
    Returns:
        Sum of possibilities across all cells
    """
    N = len(state.board)
    total = 0
    
    for r in range(N):
        for c in range(N):
            if state.board[r][c] == 0:  # Empty cell
                # Count how many values are available for this cell
                used = set()
                used.update(state.board[r])  # Row
                used.update(state.board[rr][c] for rr in range(N))  # Column
                used.discard(0)
                
                available = N - len(used)
                total += available
    
    return total


def h_inequality_violations(state: State, board: Board) -> int:
    """Count inequality constraint violations.
    
    h(s) = number of adjacent cells violating the inequality constraint
    
    Args:
        state: Current puzzle state
        board: The puzzle board with constraints
        
    Returns:
        Count of constraint violations
    """
    if not board.constraints:
        return 0
    
    violations = 0
    
    for r, c, op in board.constraints:
        # Convert to 0-indexed (constraints are 1-indexed)
        r0, c0 = r - 1, c - 1
        
        # Check horizontal constraint (cell at r, c with cell at r, c+1)
        if c0 < len(state.board[0]) - 1:
            left = state.board[r0][c0]
            right = state.board[r0][c0 + 1]
            
            if left != 0 and right != 0:  # Both filled
                if (op == '<' and left >= right) or (op == '>' and left <= right):
                    violations += 1
        
        # Check vertical constraint (cell at r, c with cell at r+1, c)
        if r0 < len(state.board) - 1:
            top = state.board[r0][c0]
            bottom = state.board[r0 + 1][c0]
            
            if top != 0 and bottom != 0:  # Both filled
                if (op == '<' and top >= bottom) or (op == '>' and top <= bottom):
                    violations += 1
    
    return violations


def h_combined(state: State, board: Board, weights: dict = None) -> int:
    """Weighted combination of multiple heuristics.
    
    Args:
        state: Current puzzle state
        board: The puzzle board
        weights: Dict of heuristic names to weights
                 Defaults to balanced weights
        
    Returns:
        Combined heuristic value
    """
    if weights is None:
        weights = {
            'remaining': 1.0,
            'constraints': 2.0,
            'inequalities': 1.5,
        }
    
    h_val = 0
    
    if weights.get('remaining', 0) > 0:
        h_val += weights['remaining'] * h_remaining_cells(state)
    
    if weights.get('constraints', 0) > 0:
        h_val += weights['constraints'] * h_constraint_violations(state, board)
    
    if weights.get('inequalities', 0) > 0:
        h_val += weights['inequalities'] * h_inequality_violations(state, board)
    
    return int(h_val)
