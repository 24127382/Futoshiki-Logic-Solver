'''
Forward chaining solver for Futoshiki puzzles.
Input State: Initial board configuration as a State object
Output State: Solved board configuration as a State object, or None if unsolvable

**Optimizations:**
- Use KB.get_unit_clauses() for O(1) unit clause lookup
- Maintain active clause set to avoid re-processing satisfied clauses
- Use deque for efficient agenda management
- Pre-compute variable-to-cell mapping for O(1) solution reconstruction
'''
from typing import Optional, Dict, Tuple
from collections import deque
from src.models.state import State
from src.models.kb import KnowledgeBase
from src.models.board import Board 

def forward_chaining_solver(initial_state: State, kb: KnowledgeBase) -> Optional[State]:
    '''
    Forward chaining based on Unit Propagation with optimizations.
    
    Args:
        initial_state: The starting state of the board
        kb: The knowledge base containing logical clauses for the puzzle
    Returns:
        A solved State if a solution is found, or None if unsolvable
    '''
    if not kb.clauses:
        # Empty KB - return initial state
        return initial_state
    
    # Pre-compute variable-to-cell mapping for O(1) solution reconstruction
    N = kb.N
    var_to_cell: Dict[int, Tuple[int, int, int]] = {}
    for r in range(1, N + 1):
        for c in range(1, N + 1):
            for v in range(1, N + 1):
                var_id = kb.get_var_id(r, c, v)
                var_to_cell[var_id] = (r, c, v)
    
    # Initialize: agenda with unit clauses (O(1) lookup now)
    unit_clauses = kb.get_unit_clauses()
    agenda = deque(unit_clauses)  # Use deque for O(1) popleft
    inferences = {}
    
    # Track each clause's unsatisfied literals
    clauses_list = [list(clause) for clause in kb.clauses]
    satisfied = [False] * len(clauses_list)
    active_clauses = set(range(len(clauses_list)))  # Track unsatisfied clauses

    while agenda:
        p = agenda.popleft()  # FIFO is better than LIFO
        
        # Skip if already inferred
        if p in inferences:
            continue
        
        # Mark as inferred
        inferences[p] = True
        
        # Only process clauses that aren't satisfied yet (optimization)
        for i in list(active_clauses):  # Iterate copy to allow modification
            clause = clauses_list[i]
            
            # If p satisfies the clause, mark it as satisfied
            if p in clause:
                satisfied[i] = True
                active_clauses.discard(i)  # Remove from active
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
    
    # Build the solved board from inferences (using pre-computed mapping)
    board = [[0] * N for _ in range(N)]
    
    for var_id in inferences:
        if var_id > 0:  # Only positive literals represent assignments
            if var_id in var_to_cell:
                r, c, v = var_to_cell[var_id]
                board[r - 1][c - 1] = v
    
    # Convert board list to tuple for State
    board_tuple = tuple(tuple(row) for row in board)
    
    return State(board_tuple, initial_state.puzzle_ref)