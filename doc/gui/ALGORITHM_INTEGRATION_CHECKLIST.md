# ALGORITHM TEAM INTEGRATION CHECKLIST

Complete this checklist to integrate your solvers with the Tkinter GUI.

## Pre-Integration (Read These)

- [ ] Read: `QUICKSTART.md` - Get oriented
- [ ] Read: `GUI_ARCHITECTURE.md` - Understand the system
- [ ] Read: `ARCHITECTURE_FLOWCHART.md` - See data flow
- [ ] Read: `SOLVER_INTEGRATION_GUIDE.py` - See examples

## Phase 1: Backtracking Solver

### Update Imports
```python
# At top of src/solvers/backtracking.py
import time
from pathlib import Path
import sys

src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models.board import Board
from gui.bridge import InputData, OutputData
```

### Checklist
- [ ] Change `solve()` signature:
  ```python
  # OLD
  def solve(self, board: Board) -> List[List[int]]:
  
  # NEW
  def solve(self, input_data: InputData) -> OutputData:
  ```

- [ ] Add timeout tracking:
  ```python
  self.start_time = time.time()
  self.iterations = 0
  ```

- [ ] Check timeout in main loop:
  ```python
  if self._check_timeout():
      return self._create_failure_output('timeout')
  
  def _check_timeout(self) -> bool:
      if time.time() - self.start_time > self.timeout:
          return True
      return False
  ```

- [ ] Track iterations:
  ```python
  # In your backtracking loop
  self.iterations += 1
  ```

- [ ] Extract data from InputData:
  ```python
  matrix = [row[:] for row in input_data.matrix]  # Copy
  constraints = input_data.constraints
  size = input_data.size
  ```

- [ ] Return OutputData on success:
  ```python
  return OutputData(
      status='success',
      solution=matrix,
      stats={
          'time_ms': (time.time() - self.start_time) * 1000,
          'iterations': self.iterations,
          'solver': 'Backtracking'
      },
      message='Puzzle solved successfully'
  )
  ```

- [ ] Return OutputData on failure:
  ```python
  return OutputData(
      status='unsolvable',
      solution=None,
      stats={
          'time_ms': (time.time() - self.start_time) * 1000,
          'iterations': self.iterations,
          'solver': 'Backtracking'
      },
      message='Puzzle is unsolvable'
  )
  ```

- [ ] Wrap in try/except:
  ```python
  try:
      # ... solve logic ...
  except Exception as e:
      return OutputData(
          status='error',
          solution=None,
          stats={'time_ms': 0, 'iterations': self.iterations},
          message=f'Error: {str(e)}'
      )
  ```

- [ ] Test locally:
  ```python
  from gui.bridge import InputData
  from src.solvers.backtracking import BacktrackingSolver
  
  input_data = InputData(
      size=4,
      matrix=[[0,0,0,1], [0,0,0,0], [0,0,0,0], [0,0,0,0]],
      constraints=[]
  )
  
  solver = BacktrackingSolver(timeout=30)
  output = solver.solve(input_data)
  
  assert output.status in ['success', 'unsolvable', 'error']
  assert output.stats['iterations'] > 0
  print(f"✓ Test passed: {output.status}")
  ```

## Phase 2: Forward Chaining Solver

### Update Imports
Same as Backtracking above

### Checklist
- [ ] Change signature from `forward_chaining_solver(state, kb)` to solver class with `solve(InputData)`
- [ ] Convert InputData → (matrix, constraints, size)
- [ ] Add timeout checking (same as backtracking)
- [ ] Track iterations count
- [ ] Return OutputData (same format as backtracking)
- [ ] Test locally

## Phase 3: A* Solver

### Update Imports
Same as Backtracking above

### Checklist
- [ ] Change signature to `solve(InputData) -> OutputData`
- [ ] Add timeout checking
- [ ] Track iterations (node expansions)
- [ ] Return OutputData
- [ ] Test locally

## Phase 4: Integrate with Controller

### Update gui/controller.py
```python
def _call_solver(self, input_data: InputData, algorithm: SolverType) -> OutputData:
    """Call the appropriate solver."""
    
    try:
        if algorithm == SolverType.BACKTRACKING:
            from src.solvers.backtracking import BacktrackingSolver
            solver = BacktrackingSolver(timeout=self.timeout_seconds)
            return solver.solve(input_data)
        
        elif algorithm == SolverType.FORWARD_CHAINING:
            from src.solvers.forward_chaining import ForwardChainingSolver
            solver = ForwardChainingSolver(timeout=self.timeout_seconds)
            return solver.solve(input_data)
        
        elif algorithm == SolverType.A_STAR:
            from src.solvers.a_star import AStarSolver
            solver = AStarSolver(timeout=self.timeout_seconds)
            return solver.solve(input_data)
        
    except Exception as e:
        return OutputData(
            status='error',
            solution=None,
            stats={'time_ms': 0, 'iterations': 0},
            message=f'Solver error: {str(e)}'
        )
```

### Checklist
- [ ] Import all solvers
- [ ] Test: Click SOLVE button in GUI
- [ ] Check: Grid fills with solution
- [ ] Check: Stats display time and iterations
- [ ] Check: Status shows "Solved"

## Phase 5: Validation

### Test Cases
```python
# Test Case 1: Small Solvable (4x4)
input_data = InputData(
    size=4,
    matrix=[[0,0,0,1], [0,2,0,0], [0,0,0,0], [4,0,0,0]],
    constraints=[((0,0), (0,1), '<')]
)
output = solver.solve(input_data)
assert output.status == 'success'
assert len(output.solution) == 4

# Test Case 2: Medium (6x6)
# ... 6x6 matrix ...
assert output.status == 'success'

# Test Case 3: Large (9x9)
# ... 9x9 matrix ...
assert output.status == 'success'

# Test Case 4: Timeout
input_data = InputData(size=9, matrix=[...], constraints=[...])
solver = BacktrackingSolver(timeout=0.001)  # 1ms timeout
output = solver.solve(input_data)
assert output.status == 'timeout'

# Test Case 5: Unsolvable
input_data = InputData(
    size=4,
    matrix=[[1,2,3,4], [0,0,0,0], [0,0,0,0], [0,0,0,0]],
    constraints=[((0,0), (0,1), '>')]  # But 1 < 2, contradiction
)
output = solver.solve(input_data)
assert output.status == 'unsolvable'
```

### Checklist
- [ ] Test 4x4 puzzle → Success
- [ ] Test 6x6 puzzle → Success
- [ ] Test 9x9 puzzle → Success (should complete in <30s)
- [ ] Test very tight timeout → Timeout status
- [ ] Test contradictory constraints → Unsolvable status
- [ ] Test malformed input → Error status
- [ ] Check all stats fields are populated
- [ ] Check GUI displays results correctly

## Phase 6: Performance

### Optimization Goals
- [ ] 4x4: < 100ms
- [ ] 6x6: < 1 second
- [ ] 9x9: < 30 seconds
- [ ] GUI remains responsive (threaded)

### Profiling
```python
import time
from gui.bridge import InputData

input_data = InputData(size=9, matrix=[...], constraints=[...])
solver = BacktrackingSolver()

start = time.time()
output = solver.solve(input_data)
elapsed = time.time() - start

print(f"Time: {elapsed:.3f}s")
print(f"Iterations: {output.stats['iterations']}")
print(f"Rate: {output.stats['iterations'] / elapsed:.0f} iter/sec")
```

### Checklist
- [ ] Profile all three algorithms
- [ ] Identify bottlenecks (usually constraint checking)
- [ ] Optimize if needed (early pruning, memoization)
- [ ] Re-test performance

## Phase 7: Documentation

### Checklist
- [ ] Add docstrings to `solve()` method
- [ ] Document input/output format
- [ ] List algorithm complexity (time, space)
- [ ] Note any assumptions or limitations
- [ ] Add usage examples

Example:
```python
def solve(self, input_data: InputData) -> OutputData:
    """
    Solve Futoshiki puzzle using backtracking.
    
    Algorithm:
    1. Find first empty cell
    2. Try values 1 to N
    3. Check constraints (row uniqueness, inequalities)
    4. Recursively solve remaining cells
    5. Backtrack on conflict
    
    Complexity:
    - Time: O(N^(N²)) worst case, O(1) best case (already solved)
    - Space: O(N²) for recursion stack
    
    Args:
        input_data: InputData with matrix and constraints
    
    Returns:
        OutputData with solution or error status
    
    Raises:
        TimeoutError: If timeout exceeded
    """
```

## Phase 8: Commit & Deploy

### Checklist
- [ ] All tests pass
- [ ] No console errors when clicking SOLVE
- [ ] GUI updates with solution
- [ ] Stats display correctly
- [ ] Code is formatted and documented
- [ ] Commit changes to git
- [ ] Update main branch

## Common Pitfalls

❌ **Don't** return List[List[int]] directly
✅ **Do** wrap in OutputData

❌ **Don't** block the main thread
✅ **Do** let Controller handle threading

❌ **Don't** modify solver for GUI-specific logic
✅ **Do** keep solver pure (math only)

❌ **Don't** ignore timeout checks
✅ **Do** check `_check_timeout()` in loops

❌ **Don't** lose iteration count
✅ **Do** increment `self.iterations` in loops

## Need Help?

1. Check: `SOLVER_INTEGRATION_GUIDE.py` for examples
2. Check: `gui/bridge.py` for InputData/OutputData definition
3. Check: `gui/controller.py` for how solver is called
4. Run: `python main.py` and click SOLVE to see actual flow
5. Add: `print()` statements to debug

## Sign-Off

When complete, mark each phase:

- [ ] Phase 1: Backtracking ✓
- [ ] Phase 2: Forward Chaining ✓
- [ ] Phase 3: A* ✓
- [ ] Phase 4: Controller Integration ✓
- [ ] Phase 5: Validation ✓
- [ ] Phase 6: Performance ✓
- [ ] Phase 7: Documentation ✓
- [ ] Phase 8: Deploy ✓

**Team Lead Sign-off Date:** _____________
