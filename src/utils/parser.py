"""Parser for Futoshiki puzzle input files.

Supports both legacy and canonical constraint formats.
"""

from typing import List, Optional, Sequence, Tuple
from src.models.state import State
from src.models.board import Board


def load_puzzle_file(filename: str) -> Tuple[Board, State]:
    """Load and parse a Futoshiki puzzle from an input file.
    
    **File Format:**
    Line 1: N (board size)
    Lines 2 to N+1: Initial board state (N space-separated integers per line)
                    0 = empty cell, 1-N = given value
     Last line: Constraints (optional)
                    Supported formats:
                    1) Legacy triplets: row col op row col op ...
                        Interpreted as horizontal constraints from (row, col) to (row, col+1)
                    2) Canonical quintuplets: r1 c1 op r2 c2 ...
                        Explicitly defines both cells in each inequality
                    where op is '<' or '>'
    
    Args:
        filename: Path to puzzle file
        
    Returns:
        Tuple of (Board, State) ready for solving
        
    Raises:
        ValueError: If file format is invalid
        IOError: If file cannot be read
    """
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    if not lines:
        raise ValueError("Empty puzzle file")
    
    # Parse board size
    try:
        N = int(lines[0])
    except ValueError:
        raise ValueError(f"First line must be board size (integer), got: {lines[0]}")
    
    if N <= 0:
        raise ValueError(f"Board size must be positive, got: {N}")
    
    # Parse initial board state
    if len(lines) < N + 1:
        raise ValueError(f"Expected {N+1} lines for board state, got {len(lines)}")
    
    initial_board = []
    for i in range(1, N + 1):
        try:
            row = tuple(map(int, lines[i].split()))
        except ValueError:
            raise ValueError(f"Line {i}: invalid board values (must be integers)")
        
        if len(row) != N:
            raise ValueError(f"Line {i}: expected {N} values, got {len(row)}")
        
        # Validate values
        for val in row:
            if not (0 <= val <= N):
                raise ValueError(f"Line {i}: value {val} out of range [0, {N}]")
        
        initial_board.append(row)
    
    initial_board = tuple(initial_board)
    
    # Parse constraints (if present)
    constraints = ()
    if len(lines) > N + 1:
        constraint_line = lines[N + 1]
        constraints = parse_constraints(constraint_line, N)
    
    # Create State and Board objects
    initial_state = State(initial_board, None)
    board = Board(N, initial_state, constraints)
    
    return board, initial_state


def parse_constraints(constraint_str: str, N: int) -> Tuple[Tuple[int, int, str, int, int], ...]:
    """Parse constraint string into constraint tuples.
    
        **Supported Formats:**
        - Legacy: row col op row col op ...
            Each triplet means (row, col) op (row, col+1)
        - Canonical: r1 c1 op r2 c2 ...
            Each quintuplet means (r1, c1) op (r2, c2)
    
    Args:
        constraint_str: Space-separated constraint specification
        N: Board size for validation
        
    Returns:
        Tuple of canonical (r1, c1, operator, r2, c2) tuples, 1-indexed
        
    Raises:
        ValueError: If constraint format is invalid
    """
    if not constraint_str:
        return ()

    parts = constraint_str.split()

    # Prefer canonical parsing when possible.
    if len(parts) % 5 == 0:
        constraints = _parse_constraints_quintuplets(parts, N)
        if constraints is not None:
            return tuple(constraints)

    if len(parts) % 3 == 0:
        return tuple(_parse_constraints_legacy_triplets(parts, N))

    raise ValueError(
        f"Invalid constraints format with {len(parts)} tokens. "
        "Use legacy triplets (row col op) or canonical quintuplets (r1 c1 op r2 c2)."
    )


def _parse_constraints_quintuplets(
    parts: Sequence[str], N: int
) -> Optional[List[Tuple[int, int, str, int, int]]]:
    constraints = []
    for i in range(0, len(parts), 5):
        try:
            r1 = int(parts[i])
            c1 = int(parts[i + 1])
            op = parts[i + 2]
            r2 = int(parts[i + 3])
            c2 = int(parts[i + 4])
        except ValueError:
            return None

        if op not in ['<', '>']:
            return None

        if not (0 <= r1 < N and 0 <= c1 < N and 0 <= r2 < N and 0 <= c2 < N):
            raise ValueError(
                f"Constraint positions ({r1}, {c1}) and ({r2}, {c2}) out of bounds for {N}x{N} board"
            )

        if abs(r1 - r2) + abs(c1 - c2) != 1:
            raise ValueError(
                f"Constraint cells must be adjacent, got ({r1}, {c1}) and ({r2}, {c2})"
            )

        constraints.append((r1 + 1, c1 + 1, op, r2 + 1, c2 + 1))

    return constraints


def _parse_constraints_legacy_triplets(
    parts: Sequence[str], N: int
) -> List[Tuple[int, int, str, int, int]]:
    constraints = []
    for i in range(0, len(parts), 3):
        try:
            r = int(parts[i])
            c = int(parts[i + 1])
            op = parts[i + 2]
        except ValueError:
            raise ValueError(f"Invalid legacy constraint at token {i}: expected (row col op)")

        if not (0 <= r < N and 0 <= c < N):
            raise ValueError(f"Constraint position ({r}, {c}) out of bounds for {N}x{N} board")

        if op not in ['<', '>']:
            raise ValueError(f"Invalid operator '{op}', must be '<' or '>'")

        # Legacy format inference:
        # - Prefer horizontal: (r,c) op (r,c+1)
        # - Fallback to vertical when horizontal is impossible: (r,c) op (r+1,c)
        if c + 1 < N:
            constraints.append((r + 1, c + 1, op, r + 1, c + 2))
        elif r + 1 < N:
            constraints.append((r + 1, c + 1, op, r + 2, c + 1))
        else:
            raise ValueError(
                f"Legacy triplet constraint ({r}, {c}, {op}) has no adjacent neighbor to infer. "
                "Use canonical format: r1 c1 op r2 c2"
            )

    return constraints


def save_solution(board: Tuple[Tuple[int, ...], ...], filename: str) -> None:
    """Save a solved board to a file.
    
    Args:
        board: Solved board as tuple of tuples
        filename: Path to output file
    """
    with open(filename, 'w') as f:
        for row in board:
            f.write(' '.join(map(str, row)) + '\n')


def format_board(board: Tuple[Tuple[int, ...], ...], title: str = "Board") -> str:
    """Format a board for pretty printing.
    
    Args:
        board: Board as tuple of tuples
        title: Optional title for the board
        
    Returns:
        Formatted board string
    """
    N = len(board)
    lines = [f"\n{title}:"]
    lines.append("+" + "-" * 3 * N + "+")
    
    for row in board:
        row_str = "|" + "|".join(str(x) if x != 0 else " " for x in row) + "|"
        lines.append(row_str)
    
    lines.append("+" + "-" * 3 * N + "+")
    return '\n'.join(lines)
