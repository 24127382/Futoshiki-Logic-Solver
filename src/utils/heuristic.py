"""Heuristic functions for informed search algorithms (A*, greedy best-first, etc.)

Provides various heuristics for estimating remaining effort in puzzle solving.
"""

from typing import Callable, Dict, Iterable, Set, Tuple
from src.models.state import State
from src.models.board import Board


ConstraintNormalized = Tuple[int, int, str, int, int]


def _iter_constraints(board: Board) -> Iterable[ConstraintNormalized]:
    """Yield constraints in normalized canonical form (r1, c1, op, r2, c2)."""
    for constraint in board.constraints:
        if len(constraint) == 3:
            r1, c1, op = constraint
            yield (r1, c1, op, r1, c1 + 1)
        elif len(constraint) == 5:
            r1, c1, op, r2, c2 = constraint
            yield (r1, c1, op, r2, c2)


def _domain_values(state: State, board: Board, r0: int, c0: int) -> Set[int]:
    """Compute legal values for an empty cell using row/column and inequality constraints."""
    N = len(state.board)

    if state.board[r0][c0] != 0:
        return {state.board[r0][c0]}

    candidates = set(range(1, N + 1))

    # Row and column uniqueness constraints.
    candidates -= {v for v in state.board[r0] if v != 0}
    candidates -= {state.board[r][c0] for r in range(N) if state.board[r][c0] != 0}

    # Inequality constraints touching this cell.
    for r1, c1, op, r2, c2 in _iter_constraints(board):
        a_r, a_c = r1 - 1, c1 - 1
        b_r, b_c = r2 - 1, c2 - 1

        if (a_r, a_c) == (r0, c0):
            other = state.board[b_r][b_c]
            if other != 0:
                if op == '<':
                    candidates = {v for v in candidates if v < other}
                else:
                    candidates = {v for v in candidates if v > other}
        elif (b_r, b_c) == (r0, c0):
            other = state.board[a_r][a_c]
            if other != 0:
                if op == '<':
                    candidates = {v for v in candidates if v > other}
                else:
                    candidates = {v for v in candidates if v < other}

    return candidates


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
    
    h(s) = sum of violated row uniqueness + column uniqueness
    
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


def h_domain_width(state: State, board: Board) -> int:
    """Domain-width heuristic for CSP-style search.

    h(s) = sum over empty cells of (|domain(cell)| - 1)

    Lower values are better. A solved board has value 0.
    """
    total = 0
    N = len(state.board)
    for r in range(N):
        for c in range(N):
            if state.board[r][c] == 0:
                domain_size = len(_domain_values(state, board, r, c))
                if domain_size == 0:
                    return 10**6
                total += domain_size - 1
    return total


def h_dead_end_penalty(state: State, board: Board, penalty: int = 10**6) -> int:
    """Large penalty for dead-end states where an empty cell has empty domain."""
    N = len(state.board)
    dead_ends = 0
    for r in range(N):
        for c in range(N):
            if state.board[r][c] != 0:
                continue
            if len(_domain_values(state, board, r, c)) == 0:
                dead_ends += 1
    return dead_ends * penalty


def h_inequality_slack(state: State, board: Board) -> int:
    """Measure remaining inequality uncertainty.

    For each inequality A op B where one side is unassigned, add the number of
    candidate values that keep the relation feasible. Lower is better.
    """
    slack = 0

    for r1, c1, op, r2, c2 in _iter_constraints(board):
        a_r, a_c = r1 - 1, c1 - 1
        b_r, b_c = r2 - 1, c2 - 1

        a_val = state.board[a_r][a_c]
        b_val = state.board[b_r][b_c]

        if a_val != 0 and b_val != 0:
            continue

        if a_val == 0 and b_val == 0:
            continue

        if a_val == 0:
            domain = _domain_values(state, board, a_r, a_c)
            if op == '<':
                slack += sum(1 for v in domain if v < b_val)
            else:
                slack += sum(1 for v in domain if v > b_val)
        else:
            domain = _domain_values(state, board, b_r, b_c)
            if op == '<':
                slack += sum(1 for v in domain if a_val < v)
            else:
                slack += sum(1 for v in domain if a_val > v)

    return slack


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
    
    for r1, c1, op, r2, c2 in _iter_constraints(board):
        left = state.board[r1 - 1][c1 - 1]
        right = state.board[r2 - 1][c2 - 1]

        if left != 0 and right != 0:
            if (op == '<' and left >= right) or (op == '>' and left <= right):
                violations += 1
    
    return violations


def h_combined(state: State, board: Board, weights: Dict[str, float] = None) -> int:
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
            'domain_width': 1.25,
            'dead_end': 1.0,
        }
    
    h_val = 0
    
    if weights.get('remaining', 0) > 0:
        h_val += weights['remaining'] * h_remaining_cells(state)
    
    if weights.get('constraints', 0) > 0:
        h_val += weights['constraints'] * h_constraint_violations(state, board)
    
    if weights.get('inequalities', 0) > 0:
        h_val += weights['inequalities'] * h_inequality_violations(state, board)

    if weights.get('domain_width', 0) > 0:
        h_val += weights['domain_width'] * h_domain_width(state, board)

    if weights.get('dead_end', 0) > 0:
        h_val += weights['dead_end'] * h_dead_end_penalty(state, board)
    
    return int(h_val)


def h_futoshiki_advanced(state: State, board: Board) -> int:
    """Default advanced heuristic for Futoshiki.

    Blends progress, domain-based complexity, inequality consistency, and hard
    dead-end penalties.
    """
    return (
        h_remaining_cells(state)
        + (2 * h_constraint_violations(state, board))
        + (2 * h_inequality_violations(state, board))
        + h_domain_width(state, board)
        + h_inequality_slack(state, board)
        + h_dead_end_penalty(state, board)
    )


HEURISTIC_REGISTRY: Dict[str, Callable[[State, Board], int]] = {
    'remaining_cells': lambda s, b: h_remaining_cells(s),
    'constraint_violations': h_constraint_violations,
    'missing_values': lambda s, b: h_missing_values(s),
    'sum_remaining_values': lambda s, b: h_sum_remaining_values(s),
    'inequality_violations': h_inequality_violations,
    'domain_width': h_domain_width,
    'inequality_slack': h_inequality_slack,
    'combined': h_combined,
    'advanced': h_futoshiki_advanced,
}


def get_heuristic(name: str) -> Callable[[State, Board], int]:
    """Resolve a heuristic by name with a safe default."""
    return HEURISTIC_REGISTRY.get(name, h_futoshiki_advanced)
