"""Knowledge base for storing logical clauses and constraints."""
from typing import Set, Tuple, List


class KnowledgeBase:
    """Stores and manages logical clauses for the Futoshiki solver.
    
    Uses a unique ID system to map board positions (row, col, value) to
    proposition identifiers for CNF formulas.
    
    **Optimizations:**
    - `clauses_by_length`: Index clauses by length for O(1) unit clause lookup
    - `var_occurrence`: Map variables to clause indices for efficient propagation
    
    Attributes:
        N: Board size (N x N)
        clauses: Set of logical clauses in CNF form
        clauses_by_length: Dict mapping clause length to list of clauses
        var_occurrence: Dict mapping variable ID to clause indices
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
        self.clauses_by_length: dict = {}  # {length: [clauses]} for fast unit clause lookup
        self.var_occurrence: dict = {}  # {var_id: [clause]} for variable propagation
    
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
        
        Maintains indexes for efficient clause lookup and variable occurrence tracking.
        
        Args:
            clause: List of proposition IDs (positive or negative for negation)
        """
        clause_tuple = tuple(clause)
        if clause_tuple in self.clauses:
            return  # Skip duplicates
        
        self.clauses.add(clause_tuple)
        
        # Index by clause length for O(1) unit clause lookup
        clause_len = len(clause_tuple)
        if clause_len not in self.clauses_by_length:
            self.clauses_by_length[clause_len] = []
        self.clauses_by_length[clause_len].append(clause_tuple)
        
        # Index variable occurrences for efficient propagation
        for var_id in clause_tuple:
            if var_id not in self.var_occurrence:
                self.var_occurrence[var_id] = []
            self.var_occurrence[var_id].append(clause_tuple)
    
    def get_unit_clauses(self) -> List[int]:
        """Get all unit clauses (single-literal clauses) efficiently.
        
        Returns:
            List of proposition IDs from unit clauses (O(1) lookup)
        """
        unit_clauses = self.clauses_by_length.get(1, [])
        return [clause[0] for clause in unit_clauses]
    
    def get_clauses_with_var(self, var_id: int) -> List[Tuple]:
        """Get all clauses containing a specific variable (for propagation).
        
        Returns:
            List of clauses containing the variable or its negation
        """
        return self.var_occurrence.get(var_id, [])
    
    def __repr__(self) -> str:
        """String representation of the knowledge base."""
        return f"KnowledgeBase(N={self.N}, clauses={len(self.clauses)})"
    
    def __len__(self) -> int:
        """Return number of clauses in the knowledge base."""
        return len(self.clauses)