"""State representation for search algorithms."""
from typing import Tuple, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.board import Board

class State:
    """Represents a state of the Futoshiki puzzle during solving.
    
    Immutable state representation suitable for use in hashing and set operations.
    
    Attributes:
        board: Immutable board configuration as nested tuple
        size: Board dimensions (size x size)
        puzzle_ref: Reference to the original puzzle board object
    """
    
    def __init__(self, board: Tuple, puzzle_ref: Optional[Any] = None) -> None:
        """Initialize a search state.
        
        Args:
            board: Board configuration as tuple of tuples (immutable)
            puzzle_ref: Reference to the original Board object for constraint checking
            
        Raises:
            ValueError: If board is not a valid tuple structure
        """
        if not isinstance(board, tuple) or not board:
            raise ValueError("Board must be a non-empty tuple of tuples")
        
        self.board = board
        self.size = len(board)
        self.puzzle_ref = puzzle_ref
    
    def __hash__(self) -> int:
        """Return hash of this state for use in sets and dictionaries."""
        return hash(self.board)
    
    def __eq__(self, other: Any) -> bool:
        """Check equality with another state based on board configuration."""
        return isinstance(other, State) and self.board == other.board
    
    def __repr__(self) -> str:
        """String representation of the state."""
        return f"State({self.size}x{self.size})"
    
    def __str__(self) -> str:
        """Human-readable state representation."""
        lines = []
        for row in self.board:
            lines.append(' '.join(str(val) if val != 0 else '.' for val in row))
        return '\n'.join(lines)
    
    def is_complete(self) -> bool:
        """Check if the board is completely filled (no zeros).
        
        Returns:
            True if every cell has a non-zero value, False otherwise
        """
        return all(val != 0 for row in self.board for val in row)