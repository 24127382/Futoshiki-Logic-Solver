"""Parser for Futoshiki puzzle input files."""

from typing import Tuple
from src.models.state import State
from src.models.board import Board

def load_puzzle_file(filename: str) -> Tuple[Board, State]:
    """
    Load and parse a Futoshiki puzzle.

    Expected format (sections separated by blank lines):
    - Line 1: N (Board Size)
    - Next N lines: Initial grid (comma-separated)
    - Next N lines: Horizontal constraints (comma-separated, 1 for <, -1 for >)
    - Next N-1 lines: Vertical constraints (comma-separated, 1 for top < bottom, -1 for top > bottom)
    """
    with open(filename, 'r') as f:
        # Read lines, strip whitespace, and completely ignore empty lines
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        raise ValueError("Empty puzzle file")

    try:
        # 1. Parse N (Board Size)
        N = int(lines[0])

        # Ensure we have exactly the right amount of data lines
        expected_lines = 1 + N + N + (N - 1) # Size + Board + Horizontal + Vertical
        if len(lines) != expected_lines:
            raise ValueError(f"Expected {expected_lines} data lines for a {N}x{N} board, but found {len(lines)}")

        # 2. Parse Initial Grid (Indices 1 to N)
        initial_board = []
        for i in range(1, N + 1):
            row = tuple(int(x.strip()) for x in lines[i].split(','))
            if len(row) != N:
                raise ValueError(f"Grid row {i} should have {N} values, found {len(row)}")
            initial_board.append(row)

        constraints = []

        # 3. Parse Horizontal Constraints (Indices N+1 to 2N)
        for r in range(N):
            line_idx = N + 1 + r
            h_vals = [int(x.strip()) for x in lines[line_idx].split(',')]
            if len(h_vals) != N - 1:
                raise ValueError(f"Horizontal constraint row {r} should have {N-1} values, found {len(h_vals)}")

            for c, val in enumerate(h_vals):
                if val == 1:
                    constraints.append((r, c, '<', r, c + 1))
                elif val == -1:
                    constraints.append((r, c, '>', r, c + 1))

        # 4. Parse Vertical Constraints (Indices 2N+1 to 3N-1)
        for r in range(N - 1):
            line_idx = 2 * N + 1 + r
            v_vals = [int(x.strip()) for x in lines[line_idx].split(',')]
            if len(v_vals) != N:
                raise ValueError(f"Vertical constraint row {r} should have {N} values, found {len(v_vals)}")

            for c, val in enumerate(v_vals):
                if val == 1:
                    constraints.append((r, c, '<', r + 1, c))
                elif val == -1:
                    constraints.append((r, c, '>', r + 1, c))

        # Freeze structures into immutable tuples
        initial_board = tuple(initial_board)
        constraints = tuple(constraints)

        initial_state = State(initial_board, None)
        board = Board(N, initial_state, constraints)

        return board, initial_state

    except ValueError as e:
        raise ValueError(f"Error parsing puzzle format: {e}")
    except IndexError:
        raise ValueError("File is missing required constraint lines.")

def save_solution(board: Tuple[Tuple[int, ...], ...], constraints: Tuple, filename: str) -> None:
    """
    Save a solved Futoshiki board with constraints to a file.
    
    Format:
    - Numbers with horizontal constraints on the same line (e.g., "2 < 3")
    - Vertical constraints on alternating rows (v for >, ^ for <)
    - Proper spacing and alignment for column readability
    
    Args:
        board: Solved 2D matrix as tuple of tuples
        constraints: Tuple of constraint tuples (r1, c1, op, r2, c2)
        filename: Output file path
    """
    N = len(board)
    
    # Build constraint maps for quick lookup
    h_constraints = {}  # (r, c) -> operator between (r,c) and (r,c+1)
    v_constraints = {}  # (r, c) -> operator between (r,c) and (r+1,c)
    
    for constraint in constraints:
        r1, c1, op, r2, c2 = constraint
        
        if r1 == r2 and c2 == c1 + 1:  # Horizontal constraint
            h_constraints[(r1, c1)] = op
        elif c1 == c2 and r2 == r1 + 1:  # Vertical constraint
            v_constraints[(r1, c1)] = op
    
    lines = []
    
    # Determine column width needed (for alignment)
    # Each cell takes: number + space + operator + space (e.g., "2 < ")
    col_width = 4  # Default width for "N < " or "N > " or "N   "
    
    for r in range(N):
        # Build the number and horizontal constraint line
        number_line = ""
        for c in range(N):
            # Add the number
            cell_str = str(board[r][c])
            number_line += cell_str
            
            # Add spacing and constraint if not the last column
            if c < N - 1:
                if (r, c) in h_constraints:
                    number_line += " " + h_constraints[(r, c)] + " "
                else:
                    number_line += "   "
        
        lines.append(number_line)
        
        # Add vertical constraint line (if not the last row)
        if r < N - 1:
            v_line = ""
            for c in range(N):
                if (r, c) in v_constraints:
                    # v for >, ^ for <
                    symbol = "v" if v_constraints[(r, c)] == ">" else "^"
                    v_line += symbol
                else:
                    v_line += " "
                
                # Add spacing to align with next column
                if c < N - 1:
                    v_line += "   "
            
            lines.append(v_line)
    
    # Write to file
    output_text = '\n'.join(lines)
    with open(filename, 'w') as f:
        f.write(output_text)
    
    # Also print to stdout
    print(output_text)

def format_board(board: Tuple[Tuple[int, ...], ...], title: str = "Board") -> str:
    """Format a board for pretty printing."""
    N = len(board)
    lines = [f"\n{title}:"]
    lines.append("+" + "-" * 3 * N + "+")

    for row in board:
        row_str = "|" + "|".join(str(x) if x != 0 else " " for x in row) + "|"
        lines.append(row_str)

    lines.append("+" + "-" * 3 * N + "+")
    return '\n'.join(lines)
