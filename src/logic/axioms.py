from src.models.kb import KnowledgeBase
from typing import List, Tuple

# Helper function to combine at_least_one and at_most_one
def exactly_one(kb: KnowledgeBase, r: int, c: int) -> List[List[int]]:
    """
    Combine at_least_one and at_most_one constraints for a single cell.
    This is more efficient for grounding: ensures cell (r,c) has exactly one value.
    
    Returns:
        List of CNF clauses for exactly_one constraint
    """
    clauses = []
    clauses.extend(at_least_one(kb, r, c))
    clauses.extend(at_most_one(kb, r, c))
    return clauses

# Box related axioms
# Each box must have at least one value
def at_least_one(kb: KnowledgeBase, r: int, c: int) -> List[List[int]]:
    clause = []
    for v in range(1, kb.N + 1):
        var_id = kb.get_var_id(r, c, v)
        clause.append(var_id)
    return [clause]  # Return list of clauses

# Each box have at most one value
def at_most_one(kb: KnowledgeBase, r: int, c: int) -> List[List[int]]:
    clauses = []
    for v1 in range(1, kb.N + 1):
        for v2 in range(v1 + 1, kb.N + 1):
            var_id1 = kb.get_var_id(r, c, v1)
            var_id2 = kb.get_var_id(r, c, v2)
            clause = [-var_id1, -var_id2]
            clauses.append(clause)
    return clauses

# -----------------------------
# Row related axioms
# Each row must have at least one value of each number 1 to N
def at_least_one_row(kb: KnowledgeBase, r: int) -> List[List[int]]:
    clauses = []
    for v in range(1, kb.N + 1):
        clause = []
        for c in range(1, kb.N + 1):
            var_id = kb.get_var_id(r, c, v)
            clause.append(var_id)
        clauses.append(clause)
    return clauses
# Each row have at most one value
def at_most_one_row(kb: KnowledgeBase, r: int) -> List[List[int]]:
    clauses = []
    for c1 in range(1, kb.N + 1):
        for c2 in range(c1 + 1, kb.N + 1):
            for v in range(1, kb.N + 1):
                var_id1 = kb.get_var_id(r, c1, v)
                var_id2 = kb.get_var_id(r, c2, v)
                clause = [-var_id1, -var_id2]
                clauses.append(clause)
    return clauses
# -----------------------------
# Column related axioms
# Each column must have at least one value of each number 1 to N
def at_least_one_col(kb: KnowledgeBase, c: int) -> List[List[int]]:
    clauses = []
    for v in range(1, kb.N + 1):
        clause = []
        for r in range(1, kb.N + 1):
            var_id = kb.get_var_id(r, c, v)
            clause.append(var_id)
        clauses.append(clause)
    return clauses
# Each column have at most one value
def at_most_one_col(kb: KnowledgeBase, c: int) -> List[List[int]]:
    clauses = []
    for r1 in range(1, kb.N + 1):
        for r2 in range(r1 + 1, kb.N + 1):
            for v in range(1, kb.N + 1):
                var_id1 = kb.get_var_id(r1, c, v)
                var_id2 = kb.get_var_id(r2, c, v)
                clause = [-var_id1, -var_id2]
                clauses.append(clause)
    return clauses

#-----------------------------
# Puzzle related axioms
# Given clues (pre-filled cells) - returns single unit clause
def given_clauses(kb: KnowledgeBase, r: int, c: int, v: int) -> List[int]:
    """Return unit clause forcing cell (r,c) to have value v.
    
    Args:
        kb: Knowledge base for variable ID mapping
        r: Row number (1-indexed)
        c: Column number (1-indexed)
        v: Value to assign
        
    Returns:
        Unit clause as list with single positive literal
    """
    var_id = kb.get_var_id(r, c, v)
    return [var_id]
# Horizontal restrictions (prevent duplicates in row for a given clue)
def horizontal_restrictions(kb: KnowledgeBase, r: int, c: int, v: int) -> List[List[int]]:
    clauses = []
    for c2 in range(1, kb.N + 1):
        if c2 != c:
            var_id = kb.get_var_id(r, c2, v)
            clause = [-var_id]
            clauses.append(clause)
    return clauses
# Vertical restrictions (prevent duplicates in column for a given clue)
def vertical_restrictions(kb: KnowledgeBase, r: int, c: int, v: int) -> List[List[int]]:
    clauses = []
    for r2 in range(1, kb.N + 1):
        if r2 != r:
            var_id = kb.get_var_id(r2, c, v)
            clause = [-var_id]
            clauses.append(clause)
    return clauses

#-----------------------------
# Inequality constraint axioms (Futoshiki specific)
def inequality_clauses(kb: KnowledgeBase, 
                       horizontal_constraints: List[Tuple[int, int, str]], 
                       vertical_constraints: List[Tuple[int, int, str]]) -> List[List[int]]:
    """
    Generate CNF clauses for inequality constraints.
    
    Args:
        kb: Knowledge base for variable ID mapping
        horizontal_constraints: List of (row, col, operator) for left cell in inequality
        vertical_constraints: List of (row, col, operator) for top cell in inequality
    
    Returns:
        List of CNF clauses forbidding invalid value combinations
    """
    clauses = []
    
    # Horizontal constraints: left_cell op right_cell
    for r, c, op in horizontal_constraints:
        # Unit clauses for optimization (OUTSIDE v1, v2 loops to avoid duplication)
        if op == '<':
            # If A < B, then A cannot be N and B cannot be 1
            clauses.append([-kb.get_var_id(r, c, kb.N)])
            clauses.append([-kb.get_var_id(r, c + 1, 1)])
        elif op == '>':
            # If A > B, then A cannot be 1 and B cannot be N
            clauses.append([-kb.get_var_id(r, c, 1)])
            clauses.append([-kb.get_var_id(r, c + 1, kb.N)])
        
        # Binary clauses forbidding invalid combinations
        for v1 in range(1, kb.N + 1):
            for v2 in range(1, kb.N + 1):
                if (op == '>' and v1 < v2) or (op == '<' and v1 > v2):
                    var_id1 = kb.get_var_id(r, c, v1)
                    var_id2 = kb.get_var_id(r, c + 1, v2)
                    clauses.append([-var_id1, -var_id2])
                    
    # Vertical constraints: top_cell op bottom_cell
    for r, c, op in vertical_constraints:
        # Unit clauses for optimization (OUTSIDE v1, v2 loops to avoid duplication)
        if op == '<':
            # If A < B, then A cannot be N and B cannot be 1
            clauses.append([-kb.get_var_id(r, c, kb.N)])
            clauses.append([-kb.get_var_id(r + 1, c, 1)])
        elif op == '>':
            # If A > B, then A cannot be 1 and B cannot be N
            clauses.append([-kb.get_var_id(r, c, 1)])
            clauses.append([-kb.get_var_id(r + 1, c, kb.N)])
        
        # Binary clauses forbidding invalid combinations
        for v1 in range(1, kb.N + 1):
            for v2 in range(1, kb.N + 1):
                if (op == '>' and v1 < v2) or (op == '<' and v1 > v2):
                    var_id1 = kb.get_var_id(r, c, v1)
                    var_id2 = kb.get_var_id(r + 1, c, v2)
                    clauses.append([-var_id1, -var_id2])
                        
    return clauses