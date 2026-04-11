'''
Forward chaining solver for Futoshiki puzzles.
Input State: Initial board configuration as a State object
Output State: Solved board configuration as a State object, or None if unsolvable
Implement function:
- forward_chaining_solver(initial_state: State) -> Optional[State]
'''
from typing import Optional
from src.models.state import State
from src.models.kb import KnowledgeBase
from src.models.board import Board 

def forward_chaining_solver(initial_state: State, kb: KnowledgeBase) -> Optional[State]:
    '''
    Forward chaining based on Unit Propagation
    
    Args:
        initial_state: The starting state of the board
        kb: The knowledge base containing logical clauses for the puzzle
    Returns:
        A solved State if a solution is found, or None if unsolvable
    '''
    if not kb.clauses:
        # Empty KB - return initial state
        return initial_state
    
    # Initialize: agenda with unit clauses
    agenda = [c[0] for c in kb.clauses if len(c) == 1]
    inferences = {}
    
    # Track each clause's unsatisfied literals
    clauses_list = [list(clause) for clause in kb.clauses]
    satisfied = [False] * len(clauses_list)

    while agenda:
        p = agenda.pop()
        
        # Skip if already inferred
        if p in inferences:
            continue
        
        # Mark as inferred
        inferences[p] = True
        
        # Process all clauses
        for i, clause in enumerate(clauses_list):
            if satisfied[i]:
                # Clause already satisfied
                continue
            
            # If p satisfies the clause, mark it as satisfied
            if p in clause:
                satisfied[i] = True
                continue
            
            # If -p is in the clause, remove it
            if -p in clause:
                clause.remove(-p)
                
                # Check for contradiction (empty clause)
                if len(clause) == 0:
                    return None
                
                # If unit clause, add to agenda
                if len(clause) == 1:
                    unit_lit = clause[0]
                    if unit_lit not in inferences and -unit_lit not in inferences:
                        agenda.append(unit_lit)
    
    # Build the solved board from inferences
    # Create a list to track variable assignments
    N = kb.N
    board = [[0] * N for _ in range(N)]
    
    # Convert inferences back to board cells
    # var_id = (r - 1) * (N ** 2) + (c - 1) * N + v
    # Reverse: given var_id, find r, c, v
    for var_id in inferences:
        if var_id > 0:  # Only positive literals represent assignments
            # var_id = (r - 1) * N^2 + (c - 1) * N + v
            adjusted_id = var_id - 1
            r_idx = adjusted_id // (N * N)
            remainder = adjusted_id % (N * N)
            c_idx = remainder // N
            v = (remainder % N) + 1
            
            r = r_idx + 1
            c = c_idx + 1
            
            if 1 <= r <= N and 1 <= c <= N and 1 <= v <= N:
                board[r - 1][c - 1] = v
    
    # Convert board list to tuple for State
    board_tuple = tuple(tuple(row) for row in board)
    
    return State(board_tuple, initial_state.puzzle_ref)