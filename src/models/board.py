
"""Board representation for Futoshiki puzzles."""
from typing import Tuple
from src.models.state import State


class Board:
    """Represents a Futoshiki puzzle board.
    
    Attributes:
        N: Size of the board (N x N grid)
        initial_state: Starting state of the board
        constraints: Tuple of inequality constraints (row, col, operator)
    """
    
    def __init__(self, N: int, initial_state: State, constraints: Tuple[Tuple[int, int, str], ...]) -> None:
        """Initialize a Futoshiki board.
        
        Args:
            N: Board size (N x N)
            initial_state: Starting board state
            constraints: Inequality constraints as (row, col, operator) tuples
                        operator can be '<', '>', '<=', or '>='
        
        Raises:
            ValueError: If N is not positive or constraints are invalid
        """
        if N <= 0:
            raise ValueError(f"Board size N must be positive, got {N}")
        
        self.N = N
        self.initial_state = initial_state
        self.constraints = constraints
    
    def __repr__(self) -> str:
        """String representation of the board."""
        return f"Board(N={self.N}, constraints={len(self.constraints)})" 
    
    def __str__(self) -> str:
        """Human-readable board representation."""
        return f"Futoshiki Board {self.N}x{self.N} with {len(self.constraints)} constraints"