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
    
    **Optimizations:**
    - Skip grounding cells already filled in initial state
    - Only ground unfilled cells to reduce clause explosion
    
    This function iterates over all cells, rows, and columns of the board, grounding the relevant axioms for each.
    It also grounds puzzle-specific axioms like given clues and inequality constraints.
    It adds the resulting CNF clauses to the knowledge base.
    
    Args:
        kb: The knowledge base to which grounded clauses will be added
        board: The Futoshiki puzzle board with initial state and constraints
    """
    initial_board = board.initial_state.board
    
    # Ground box axioms for each UNFILLED cell (skip pre-filled cells)
    for r in range(1, kb.N + 1):
        for c in range(1, kb.N + 1):
            # Use optimized partial grounding
            clauses = exactly_one_partial(kb, r, c, initial_board)
            for clause in clauses:
                kb.add_clause(clause)
    
    # Ground row axioms for each row (optimized for unfilled cells)
    for r in range(1, kb.N + 1):
        clauses = at_least_one_row(kb, r)
        for clause in clauses:
            kb.add_clause(clause)
        # Use optimized at_most_one that skips filled cells
        clauses = at_most_one_row_partial(kb, r, initial_board)
        for clause in clauses:
            kb.add_clause(clause)
            
    # Ground column axioms for each column (optimized for unfilled cells)
    for c in range(1, kb.N + 1):
        clauses = at_least_one_col(kb, c)
        for clause in clauses:
            kb.add_clause(clause)
        # Use optimized at_most_one that skips filled cells
        clauses = at_most_one_col_partial(kb, c, initial_board)
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
        if len(constraint) == 3:
            # Legacy format: (row, col, op) means horizontal: (r,c) op (r,c+1)
            r, c, op = constraint
            if not (1 <= r <= kb.N and 1 <= c < kb.N):
                raise ValueError(
                    f"Invalid legacy inequality constraint {constraint} for board size {kb.N}"
                )
            h_constraints.append((r, c, op))
            continue

        if len(constraint) != 5:
            raise ValueError(
                "Inequality constraints must be (r,c,op) or (r1,c1,op,r2,c2) tuples"
            )

        r1, c1, op, r2, c2 = constraint
        if op not in ['<', '>']:
            raise ValueError(f"Invalid inequality operator '{op}' in constraint {constraint}")

        if abs(r1 - r2) + abs(c1 - c2) != 1:
            raise ValueError(f"Constraint cells must be adjacent: {constraint}")

        # Normalize to left->right or top->bottom orientation expected by inequality_clauses.
        if r1 == r2:
            if c1 < c2:
                h_constraints.append((r1, c1, op))
            else:
                flipped_op = '<' if op == '>' else '>'
                h_constraints.append((r2, c2, flipped_op))
        elif c1 == c2:
            if r1 < r2:
                v_constraints.append((r1, c1, op))
            else:
                flipped_op = '<' if op == '>' else '>'
                v_constraints.append((r2, c2, flipped_op))
        else:
            raise ValueError(f"Unsupported constraint orientation: {constraint}")
    
    # Generate and add inequality clauses
    ineq_clauses = inequality_clauses(kb, h_constraints, v_constraints)
    for clause in ineq_clauses:
        kb.add_clause(clause)
            
            
