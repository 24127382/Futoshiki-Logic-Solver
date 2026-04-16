
"""Board representation for Futoshiki puzzles."""
from typing import Tuple, Union
from src.models.state import State


Constraint3 = Tuple[int, int, str]
Constraint5 = Tuple[int, int, str, int, int]
Constraint = Union[Constraint3, Constraint5]


class Board:
    """Represents a Futoshiki puzzle board.
    
    Attributes:
        N: Size of the board (N x N grid)
        initial_state: Starting state of the board
        constraints: Tuple of inequality constraints
    """
    
    def __init__(self, N: int, initial_state: State, constraints: Tuple[Constraint, ...]) -> None:
        """Initialize a Futoshiki board.
        
        Args:
            N: Board size (N x N)
            initial_state: Starting board state
            constraints: Inequality constraints in one of two forms:
                        - Legacy: (row, col, operator)
                        - Canonical: (row1, col1, operator, row2, col2)
                        operator can be '<' or '>'
        
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