"""Knowledge base for storing logical clauses and constraints."""
from typing import Set, Tuple, List


class KnowledgeBase:
    """Stores and manages logical clauses for the Futoshiki solver.
    
    Uses a unique ID system to map board positions (row, col, value) to
    proposition identifiers for CNF formulas.
    
    Attributes:
        N: Board size (N x N)
        clauses: Set of logical clauses in CNF form
    """
    
    def __init__(self, N: int) -> None:
        """Initialize a knowledge base.
        
        Args:
            N: Board size (N x N)
            
        Raises:
            ValueError: If N is not positive
        """
        if N <= 0:
            raise ValueError(f"Board size N must be positive, got {N}")
        self.N = N
        self.clauses: Set[Tuple] = set()
    
    def _get_id(self, r: int, c: int, v: int) -> int:
        """Convert board position and value to unique proposition ID.
        
        Maps (row, col, value) to a unique integer for use in logical formulas.
        Uses the formula: (r-1) * N² + (c-1) * N + v
        
        Args:
            r: Row number (1 to N)
            c: Column number (1 to N)
            v: Value (1 to N)
            
        Returns:
            Unique integer ID for the proposition (row=r, col=c, value=v)
        """
        if not (1 <= r <= self.N and 1 <= c <= self.N and 1 <= v <= self.N):
            raise ValueError(f"Invalid coordinates: r={r}, c={c}, v={v} for N={self.N}")
        return (r - 1) * (self.N ** 2) + (c - 1) * self.N + v
    
    def get_var_id(self, r: int, c: int, v: int) -> int:
        """Public method to get variable ID for a cell position and value.
        
        Args:
            r: Row number (1 to N)
            c: Column number (1 to N)
            v: Value (1 to N)
            
        Returns:
            Unique integer ID for the proposition (row=r, col=c, value=v)
        """
        return self._get_id(r, c, v)
    
    def add_clause(self, clause: List[int]) -> None:
        """Add a logical clause to the knowledge base.
        
        Args:
            clause: List of proposition IDs (positive or negative for negation)
        """
        self.clauses.add(tuple(clause))
    
    def __repr__(self) -> str:
        """String representation of the knowledge base."""
        return f"KnowledgeBase(N={self.N}, clauses={len(self.clauses)})"
    
    def __len__(self) -> int:
        """Return number of clauses in the knowledge base."""
        return len(self.clauses)