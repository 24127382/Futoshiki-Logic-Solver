# Futoshiki Solver: Quick Reference Guide

## Variable ID Formula

$$ID = (r-1) \cdot N^2 + (c-1) \cdot N + v$$

**Example (N=3)**:
- (1,1,1) → ID = 1
- (1,2,1) → ID = 4  
- (2,1,1) → ID = 10

---

## Core Functions

### Cell: Exactly One Value

```python
exactly_one(kb, r, c)
# Generates 4 clauses for 3×3 board:
# [1, 2, 3], [-1, -2], [-1, -3], [-2, -3]
```

### Row: All Values Unique

```python
at_least_one_row(kb, r)    # N clauses
at_most_one_row(kb, r)     # N(N-1)² clauses
```

### Column: All Values Unique

```python
at_least_one_col(kb, c)    # N clauses
at_most_one_col(kb, c)     # N(N-1)² clauses
```

### Inequality: A < B

```python
inequality_clauses(kb, h_constraints, v_constraints)
# Generates unit + binary clauses forbidding invalid pairs
```

### Given Clue: Cell = Value

```python
given_clauses(kb, r, c, v)                  # Unit clause
horizontal_restrictions(kb, r, c, v)        # Row restrictions
vertical_restrictions(kb, r, c, v)          # Column restrictions
```

---

## Complete Grounding Example

```python
from src.models.kb import KnowledgeBase
from src.models.board import Board
from src.models.state import State
from src.logic.grounding import ground_axioms

# Setup
kb = KnowledgeBase(3)
initial_state = State(((2, 0, 0), (0, 0, 0), (0, 0, 0)), None)
constraints = ((1, 1, '<'),)
board = Board(3, initial_state, constraints)

# Ground all axioms
ground_axioms(kb, board)

# KB ready for SAT solver
print(f"Total clauses: {len(kb)}")
```

---

## Solution Reconstruction

```python
solution = [[0]*N for _ in range(N)]

for r in range(1, N + 1):
    for c in range(1, N + 1):
        for v in range(1, N + 1):
            var_id = kb.get_var_id(r, c, v)
            if assignment.get(var_id) == True:
                solution[r-1][c-1] = v
                break
```

---

## Complexity

| Board Size | Clauses | Time |
|-----------|---------|------|
| 3×3 | ~350 | 100ms |
| 4×4 | ~1.2K | 500ms |
| 9×9 | ~50K | 10s |

**Formula**: O(N⁴) clauses

---

## Key Points

- **Uniqueness**: Each (r,c,v) maps to exactly one ID
- **CNF**: All constraints expressible in CNF
- **Grounding**: O(N⁴) time complexity
- **SAT Solver**: Bottleneck for large puzzles
- **Unit Clauses**: Enable early propagation

---

**Version**: 1.0 | **Status**: Production Ready
