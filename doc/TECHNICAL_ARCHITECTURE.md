# Technical Architecture: Futoshiki Solver

## Overview: From Puzzle to SAT Problem

The **Futoshiki Solver** transforms logic puzzles into **Boolean Satisfiability (SAT) problems** using **Propositional Logic with Conjunctive Normal Form (CNF)**.

### System Transformation Pipeline

```
Input Puzzle → Parser → Board → Knowledge Base (Empty)
                                       ↓
                                  Grounding Engine
                                   ↙ ↓ ↘
                            Axioms Inequalities Givens
                                   ↖ ↓ ↗
                            Knowledge Base (Populated)
                                       ↓
                                  SAT Solver
                                       ↓
                            Solution Variables
                                       ↓
                            Solution Board
```

---

## Part 1: Variable Mapping (Knowledge Base)

### The Formula: Unique Variable IDs

$$ID = (r-1) \cdot N^2 + (c-1) \cdot N + v$$

Where:
- **r** = Row (1 to N)
- **c** = Column (1 to N)  
- **v** = Value (1 to N)
- **N** = Board size

### Why It Works

1. **Uniqueness**: Each (r,c,v) → exactly one integer
2. **Ordering**: IDs increase monotonically
3. **Efficiency**: O(1) lookup, minimal memory

### Example (3×3)

| (r,c) | v=1 | v=2 | v=3 |
|-------|-----|-----|-----|
| (1,1) | 1   | 2   | 3   |
| (1,2) | 4   | 5   | 6   |
| (1,3) | 7   | 8   | 9   |
| (2,1) | 10  | 11  | 12  |

---

## Part 2: Axioms (Logical Rules)

### Cell Axiom: Exactly One Value

**Logic**: Each cell contains exactly one value (1 to N)

**CNF Clauses**:
- **At-least-one**: $(v_1 \vee v_2 \vee \ldots \vee v_n)$
- **At-most-one**: $(\neg v_i \vee \neg v_j)$ for all $i < j$

```python
def exactly_one(kb, r, c):
    clauses = []
    # At-least-one clause
    clause = [kb.get_var_id(r, c, v) for v in range(1, kb.N + 1)]
    clauses.append(clause)
    
    # At-most-one clauses
    for v1 in range(1, kb.N + 1):
        for v2 in range(v1 + 1, kb.N + 1):
            clauses.append([-kb.get_var_id(r, c, v1), 
                           -kb.get_var_id(r, c, v2)])
    return clauses
```

### Row Axiom: All Numbers Unique

**Logic**: Each value appears exactly once per row

```python
def at_least_one_row(kb, r):
    """Each value must appear in row r"""
    clauses = []
    for v in range(1, kb.N + 1):
        clause = [kb.get_var_id(r, c, v) for c in range(1, kb.N + 1)]
        clauses.append(clause)
    return clauses

def at_most_one_row(kb, r):
    """No value appears twice in row r"""
    clauses = []
    for c1 in range(1, kb.N + 1):
        for c2 in range(c1 + 1, kb.N + 1):
            for v in range(1, kb.N + 1):
                var_id1 = kb.get_var_id(r, c1, v)
                var_id2 = kb.get_var_id(r, c2, v)
                clauses.append([-var_id1, -var_id2])
    return clauses
```

### Column Axiom: All Numbers Unique

**Identical to row axiom, but across columns**

```python
def at_least_one_col(kb, c):
    """Each value must appear in column c"""
    clauses = []
    for v in range(1, kb.N + 1):
        clause = [kb.get_var_id(r, c, v) for r in range(1, kb.N + 1)]
        clauses.append(clause)
    return clauses

def at_most_one_col(kb, c):
    """No value appears twice in column c"""
    clauses = []
    for r1 in range(1, kb.N + 1):
        for r2 in range(r1 + 1, kb.N + 1):
            for v in range(1, kb.N + 1):
                var_id1 = kb.get_var_id(r1, c, v)
                var_id2 = kb.get_var_id(r2, c, v)
                clauses.append([-var_id1, -var_id2])
    return clauses
```

---

## Part 3: Inequality Constraints

### Converting A < B to CNF

For cells with constraint A < B:
- **A cannot be max**: $\neg ID_{A,N}$
- **B cannot be 1**: $\neg ID_{B,1}$
- **Forbidden pairs**: $(\neg ID_{A,v1} \vee \neg ID_{B,v2})$ when $v1 \ge v2$

```python
def inequality_clauses(kb, h_constraints, v_constraints):
    """Generate clauses for inequality constraints"""
    clauses = []
    
    # Horizontal constraints: left_cell op right_cell
    for r, c, op in h_constraints:
        if op == '<':
            # A < B
            clauses.append([-kb.get_var_id(r, c, kb.N)])
            clauses.append([-kb.get_var_id(r, c + 1, 1)])
        elif op == '>':
            # A > B
            clauses.append([-kb.get_var_id(r, c, 1)])
            clauses.append([-kb.get_var_id(r, c + 1, kb.N)])
        
        # Binary clauses for forbidden pairs
        for v1 in range(1, kb.N + 1):
            for v2 in range(1, kb.N + 1):
                if (op == '>' and v1 < v2) or (op == '<' and v1 > v2):
                    var_id1 = kb.get_var_id(r, c, v1)
                    var_id2 = kb.get_var_id(r, c + 1, v2)
                    clauses.append([-var_id1, -var_id2])
    
    return clauses
```

---

## Part 4: Given Clues

### Forcing Cell Values

For pre-filled cell (r,c) = v:

```python
def given_clauses(kb, r, c, v):
    """Unit clause: cell must have this value"""
    return [kb.get_var_id(r, c, v)]

def horizontal_restrictions(kb, r, c, v):
    """No other cell in row can have this value"""
    clauses = []
    for c2 in range(1, kb.N + 1):
        if c2 != c:
            clauses.append([-kb.get_var_id(r, c2, v)])
    return clauses

def vertical_restrictions(kb, r, c, v):
    """No other cell in column can have this value"""
    clauses = []
    for r2 in range(1, kb.N + 1):
        if r2 != r:
            clauses.append([-kb.get_var_id(r2, c, v)])
    return clauses
```

---

## Part 5: The Grounding Process

### What is Grounding?

Grounding converts abstract axiom templates into concrete CNF clauses by iterating through all cells, rows, columns, and constraints.

### Complete Grounding Algorithm

```python
def ground_axioms(kb, board):
    """Ground all axioms into Knowledge Base"""
    
    # 1. Cell constraints (exactly one per cell)
    for r in range(1, kb.N + 1):
        for c in range(1, kb.N + 1):
            for clause in exactly_one(kb, r, c):
                kb.add_clause(clause)
    
    # 2. Row constraints
    for r in range(1, kb.N + 1):
        for clause in at_least_one_row(kb, r):
            kb.add_clause(clause)
        for clause in at_most_one_row(kb, r):
            kb.add_clause(clause)
    
    # 3. Column constraints
    for c in range(1, kb.N + 1):
        for clause in at_least_one_col(kb, c):
            kb.add_clause(clause)
        for clause in at_most_one_col(kb, c):
            kb.add_clause(clause)
    
    # 4. Given clues
    ground_given_clues(kb, board)
    
    # 5. Inequality constraints
    ground_inequality_constraints(kb, board)
```

---

## Part 6: Complete Workflow

### Step-by-Step Example

```python
# Step 1: Create Knowledge Base
kb = KnowledgeBase(3)

# Step 2: Create Board
initial_state = State(((2, 0, 0), (0, 0, 0), (0, 0, 0)), None)
constraints = ((1, 1, '<'),)  # Cell (1,1) < Cell (1,2)
board = Board(3, initial_state, constraints)

# Step 3: Ground All Axioms
ground_axioms(kb, board)
# KB now contains ~300+ clauses

# Step 4: SAT Solver (your implementation)
solver = MySATSolver(kb)
assignment = solver.solve()
# assignment = {1: True, 2: True, 3: False, ...}

# Step 5: Reconstruct Solution
solution = [[0]*3 for _ in range(3)]
for r in range(1, 4):
    for c in range(1, 4):
        for v in range(1, 4):
            var_id = kb.get_var_id(r, c, v)
            if assignment.get(var_id) == True:
                solution[r-1][c-1] = v
                break

print(solution)
# Output: Solution board
```

---

## Complexity Analysis

For an **N×N** Futoshiki puzzle:

| Component | Clauses | Formula |
|-----------|---------|---------|
| Cell (exactly-one) | $N^2$ | $N^2 + \frac{N^4-N^3}{2}$ |
| Row (all unique) | $3N^2$ | $3N^4 - 3N^3$ |
| Column (all unique) | $3N^2$ | $3N^4 - 3N^3$ |
| **Total** | | **O(N⁴)** |

**Examples**:
- 3×3: ~350 clauses
- 4×4: ~1,200 clauses
- 9×9: ~50,000 clauses

---

**Documentation Version**: 1.0 | **Status**: Production Ready
