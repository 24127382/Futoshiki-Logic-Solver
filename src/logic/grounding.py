'''
This module contains the logic for grounding axioms in a knowledge base.
Grounding is the process of converting high-level logical axioms into specific CNF clauses that can be used by a SAT solver.
'''

from src.logic.axioms import *
from src.models.kb import KnowledgeBase
from src.models.board import Board
from typing import List, Tuple

def ground_axioms(kb: KnowledgeBase, board: Board) -> None:
    """Ground all axioms into the knowledge base.
    
    This function iterates over all cells, rows, and columns of the board, grounding the relevant axioms for each.
    It also grounds puzzle-specific axioms like given clues and inequality constraints.
    It adds the resulting CNF clauses to the knowledge base.
    
    Args:
        kb: The knowledge base to which grounded clauses will be added
        board: The Futoshiki puzzle board with initial state and constraints
    """
    # Ground box axioms for each cell (exactly one value per cell)
    for r in range(1, kb.N + 1):
        for c in range(1, kb.N + 1):
            clauses = exactly_one(kb, r, c)
            for clause in clauses:
                kb.add_clause(clause)
    
    # Ground row axioms for each row
    for r in range(1, kb.N + 1):
        clauses = at_least_one_row(kb, r)
        for clause in clauses:
            kb.add_clause(clause)
        clauses = at_most_one_row(kb, r)
        for clause in clauses:
            kb.add_clause(clause)
            
    # Ground column axioms for each column
    for c in range(1, kb.N + 1):
        clauses = at_least_one_col(kb, c)
        for clause in clauses:
            kb.add_clause(clause)
        clauses = at_most_one_col(kb, c)
        for clause in clauses:
            kb.add_clause(clause)
    
    # Ground given clues (pre-filled cells in initial state)
    ground_given_clues(kb, board)
    
    # Ground inequality constraints (Futoshiki specific)
    ground_inequality_constraints(kb, board)


def ground_given_clues(kb: KnowledgeBase, board: Board) -> None:
    """Ground given clues from the initial board state.
    
    For each pre-filled cell in the initial state, add unit clauses to fix its value
    and add restrictions to prevent duplicates in the same row/column.
    
    Args:
        kb: The knowledge base to which clauses will be added
        board: The board containing the initial state with given clues
    """
    for r in range(board.N):
        for c in range(board.N):
            value = board.initial_state.board[r][c]
            if value != 0:  # Pre-filled cell (1-indexed in axioms)
                v = value
                r_idx = r + 1  # Convert to 1-indexed
                c_idx = c + 1
                
                # Add unit clause: this cell must have this value
                clause = given_clauses(kb, r_idx, c_idx, v)
                kb.add_clause(clause)
                
                # Add restrictions: no other cell in same row/column can have this value
                h_restrictions = horizontal_restrictions(kb, r_idx, c_idx, v)
                for restriction in h_restrictions:
                    kb.add_clause(restriction)
                
                v_restrictions = vertical_restrictions(kb, r_idx, c_idx, v)
                for restriction in v_restrictions:
                    kb.add_clause(restriction)


def ground_inequality_constraints(kb: KnowledgeBase, board: Board) -> None:
    """Ground inequality constraints from the puzzle.
    
    Convert the board's constraint tuples into CNF clauses and add them to the KB.
    
    Args:
        kb: The knowledge base to which clauses will be added
        board: The board containing inequality constraints
    """
    if not board.constraints:
        return
    
    # Separate constraints into horizontal and vertical
    h_constraints = []
    v_constraints = []
    
    for constraint in board.constraints:
        # Assuming constraint format: (row, col, operator)
        # where row,col is the position of the left/top cell
        r, c, op = constraint
        if op in ['<', '>']:  # Horizontal constraints would be adjacent columns
            # This needs clarification based on how constraints are parsed
            # For now, assuming they're already separated or will be
            pass
    
    # Generate and add inequality clauses
    ineq_clauses = inequality_clauses(kb, h_constraints, v_constraints)
    for clause in ineq_clauses:
        kb.add_clause(clause)
            
            
