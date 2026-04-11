# Futoshiki Solver - Unit Testing Guide

## Overview

The Futoshiki Solver project includes comprehensive unit tests covering all core models and their functionality. The test suite is organized into two main test modules with 67 total tests.

## Test Suite Structure

### 📊 Test Statistics

- **Total Tests:** 67
- **All Passing:** ✅ 100% (67/67)
- **Execution Time:** ~16ms
- **Test Modules:** 2
- **Test Classes:** 10

### Test Modules

#### 1. **test_models.py** (45 tests)
Core functionality tests for all models

- **TestBoard** (8 tests)
  - Valid/invalid initialization
  - Constraint handling
  - String representations

- **TestKnowledgeBase** (17 tests)
  - Initialization and validation
  - Variable ID generation and formula verification
  - Clause management and deduplication
  - Error handling and boundary checking

- **TestState** (19 tests)
  - State creation and validation
  - Hashing and equality for use in search algorithms
  - String representations with proper formatting
  - Completion detection logic
  - Immutability enforcement

- **TestIntegration** (2 tests)
  - Multi-component interaction
  - Resource sharing across components

#### 2. **test_models_advanced.py** (22 tests)
Advanced scenarios and edge cases

- **TestBoundaryConditions** (5 tests)
  - Large board handling
  - Extreme value testing
  - Monotonicity verification

- **TestComplexScenarios** (4 tests)
  - Large clause sets
  - Complex state equality
  - Component reusability

- **TestErrorRecovery** (2 tests)
  - Graceful error handling
  - State recovery

- **TestSpecialCases** (4 tests)
  - Special values and edge cases
  - Unusual board configurations

- **TestConsistency** (5 tests)
  - Hash and equality consistency
  - Reflexive, symmetric, and transitive properties

- **TestPerformance** (2 tests)
  - ID generation performance
  - String representation efficiency

## Running the Tests

### Option 1: Run All Tests Together
```bash
python experiments/run_tests.py
```

This runs all 67 tests with a comprehensive summary report.

### Option 2: Run Specific Test Module
```bash
# Run just the basic models tests
python -m unittest experiments.test_models -v

# Run just the advanced tests
python -m unittest experiments.test_models_advanced -v
```

### Option 3: Run Specific Test Class
```bash
# Run all Board tests
python -m unittest experiments.test_models.TestBoard -v

# Run all KnowledgeBase tests
python -m unittest experiments.test_models.TestKnowledgeBase -v

# Run all State tests
python -m unittest experiments.test_models.TestState -v

# Run boundary condition tests
python -m unittest experiments.test_models_advanced.TestBoundaryConditions -v
```

### Option 4: Run Specific Test Method
```bash
# Test board initialization
python -m unittest experiments.test_models.TestBoard.test_board_initialization_valid -v

# Test KB variable ID formula
python -m unittest experiments.test_models.TestKnowledgeBase.test_get_var_id_formula_correctness -v

# Test state completion
python -m unittest experiments.test_models.TestState.test_is_complete_full_board -v
```

## Test Coverage Details

### Board Model (`src/models/board.py`)

| Feature | Test Cases | Coverage |
|---------|-----------|----------|
| Initialization | 4 | ✅ Valid/Invalid sizes (1, 3, 5, negative, zero) |
| Constraints | 2 | ✅ With/without constraints |
| Validation | 4 | ✅ Size validation, error messages |
| String Output | 2 | ✅ __repr__ and __str__ methods |

### Knowledge Base Model (`src/models/kb.py`)

| Feature | Test Cases | Coverage |
|---------|-----------|----------|
| Initialization | 3 | ✅ Valid/Invalid N values |
| Variable ID Generation | 10 | ✅ Formula correctness, boundaries, invalid inputs |
| Clause Management | 5 | ✅ Single/Multiple clauses, duplicates, negation |
| Error Handling | 5 | ✅ Invalid coordinates, recovery |
| String Output | 2 | ✅ __repr__ and __len__ |

### State Model (`src/models/state.py`)

| Feature | Test Cases | Coverage |
|---------|-----------|----------|
| Initialization | 4 | ✅ Valid/Invalid tuple structures |
| Hashing | 3 | ✅ Hash consistency, set operations |
| Equality | 4 | ✅ Equality, non-State comparisons, reflexivity |
| String Output | 4 | ✅ Different board states, formatting |
| Completion Detection | 5 | ✅ Empty/Partial/Complete boards |
| Immutability | 1 | ✅ Tuple immutability |

## Testing Patterns Used

### 1. **Happy Path Testing**
Tests valid inputs and expected behavior:
```python
def test_board_initialization_valid(self):
    board = Board(3, initial_state, constraints)
    self.assertEqual(board.N, 3)
```

### 2. **Boundary Testing**
Tests edge cases and limits:
```python
def test_kb_get_var_id_boundary_values(self):
    id_1_1_1 = kb.get_var_id(1, 1, 1)      # Top-left
    id_3_3_3 = kb.get_var_id(3, 3, 3)      # Bottom-right
```

### 3. **Error Handling Testing**
Tests invalid inputs and error recovery:
```python
def test_board_invalid_size_zero(self):
    with self.assertRaises(ValueError):
        Board(0, state, constraints)
```

### 4. **Integration Testing**
Tests component interaction:
```python
def test_board_with_state_and_kb(self):
    state = State(board, None)
    board = Board(3, state, constraints)
    kb = KnowledgeBase(3)
    # Verify all work together
```

### 5. **Property-Based Testing**
Tests mathematical properties:
```python
def test_kb_variable_id_monotonicity(self):
    # Verify IDs increase monotonically
    for r, c, v: self.assertGreater(current_id, previous_id)
```

### 6. **Consistency Testing**
Tests consistency of operations:
```python
def test_state_equality_symmetry(self):
    self.assertEqual(state1, state2)
    self.assertEqual(state2, state1)  # A=B implies B=A
```

## Understanding the Test Results

### Success Output
```
Ran 67 tests in 0.016s
OK

Passed:  67 ✓
Failed:  0 ✗
Success Rate: 100.0%
```

### Failure Output
If a test fails, you'll see:
```
FAIL: test_board_initialization_valid (...)
AssertionError: 3 != 5  # Actual != Expected
```

## Key Test Assertions

### Equality Assertions
```python
self.assertEqual(board.N, 3)           # Check exact values
self.assertNotEqual(state1, state2)    # Check difference
```

### Membership Assertions
```python
self.assertIn("Board", repr_string)    # Check substring
self.assertTrue(state.is_complete())   # Check boolean
self.assertFalse(state.is_complete())  # Check boolean
```

### Error Assertions
```python
with self.assertRaises(ValueError):
    Board(0, state, constraints)  # Expect ValueError
```

### Collection Assertions
```python
self.assertEqual(len(kb), 3)           # Check length
state_set = {state1, state2, state3}   # Test hashability
```

## Continuous Testing Recommendations

### Before Committing
```bash
python experiments/run_tests.py
```
All tests should pass with 100% success rate.

### During Development
Monitor specific test classes related to your changes:
```bash
python -m unittest experiments.test_models.TestBoard -v
```

### Performance Regression Testing
The advanced tests include performance checks:
```bash
python -m unittest experiments.test_models_advanced.TestPerformance -v
```

## Extending the Tests

To add new test cases:

1. **Choose the appropriate test file:**
   - Use `test_models.py` for core functionality
   - Use `test_models_advanced.py` for edge cases

2. **Create a test method:**
```python
def test_new_feature(self):
    """Test description."""
    # Setup
    obj = MyClass(param)
    
    # Execute
    result = obj.method()
    
    # Assert
    self.assertEqual(result, expected)
```

3. **Run and verify:**
```bash
python -m unittest experiments.test_models.TestBoard.test_new_feature -v
```

## Troubleshooting

### Tests fail to import modules
**Solution:** Ensure you're running from the project root directory (`d:\study\projects-new\futoshiki-solver\`)

### Module not found errors
**Solution:** The test runner automatically adds the parent directory to Python path

### Individual test passes but test suite fails
**Solution:** Check for test interdependencies or shared state issues

## Test Maintenance

- Tests should be updated when APIs change
- Add tests for new features before implementation (TDD)
- Keep tests focused on single functionality
- Use descriptive test names and docstrings
- Maintain test independence (no shared state)

---

**Last Updated:** 2026-04-10  
**Total Test Coverage:** 67 tests covering Board, KnowledgeBase, and State models  
**All Tests Status:** ✅ PASSING (100%)
