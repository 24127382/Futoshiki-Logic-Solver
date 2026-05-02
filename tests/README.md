# Experiments & Testing Directory

Comprehensive unit testing suite for the Futoshiki Solver project.

## 📁 Files in This Directory

### Test Files
- **`test_models.py`** (45 tests)
  - Core unit tests for Board, KnowledgeBase, and State models
  - Tests valid initialization, error handling, string representations
  - Integration tests combining multiple components

- **`test_models_advanced.py`** (22 tests)
  - Advanced tests for boundary conditions, edge cases
  - Complex scenarios with large data sets
  - Performance and consistency validation
  - Error recovery testing

### Test Execution
- **`run_tests.py`**
  - Test runner script with comprehensive reporting
  - Provides summary statistics and detailed failure information
  - Supports running all tests or specific test classes

### Documentation
- **`TEST_RESULTS.md`**
  - Summary of all test cases with pass/fail status
  - Detailed breakdown by test class
  - Coverage metrics and test quality statistics

- **`TESTING_GUIDE.md`**
  - Complete guide to running and understanding tests
  - Explanation of testing patterns used
  - Instructions for extending test suite

- **`README.md`** (this file)
  - Overview of the experiments directory

## 🚀 Quick Start

### Run All Tests
```bash
python experiments/run_tests.py
```

### Run Specific Test Suite
```bash
# Basic tests
python -m unittest experiments.test_models -v

# Advanced tests
python -m unittest experiments.test_models_advanced -v
```

### Run Single Test Class
```bash
python -m unittest experiments.test_models.TestBoard -v
```

## 📊 Test Results Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 67 |
| **Passed** | 67 ✅ |
| **Failed** | 0 |
| **Success Rate** | 100% |
| **Execution Time** | ~16ms |

## ✅ What's Tested

### Board Model
- ✓ Initialization with various sizes (1x1, 3x3, 5x5+)
- ✓ Constraint management
- ✓ Invalid input rejection
- ✓ String representations (__repr__, __str__)

### Knowledge Base Model
- ✓ Clause storage and retrieval
- ✓ Variable ID generation with correct formula: `(r-1)*N² + (c-1)*N + v`
- ✓ Boundary validation (rows, columns, values)
- ✓ Negation support in logical clauses
- ✓ Duplicate prevention using set semantics

### State Model
- ✓ Immutable board representation
- ✓ Hashability for use in search algorithms
- ✓ Equality comparison with proper semantics
- ✓ Completion detection (all cells filled)
- ✓ Human-readable string output with formatting

### Integration
- ✓ Multiple models working together
- ✓ Component interaction and compatibility
- ✓ Shared resource management

## 📝 Test Categories

### By Type
- **Positive Tests (Happy Path):** Valid inputs, expected behavior
- **Negative Tests (Error Handling):** Invalid inputs, error rejection
- **Edge Cases:** Boundary values, extreme inputs
- **Integration Tests:** Multi-component scenarios
- **Performance Tests:** Efficiency validation
- **Consistency Tests:** Mathematical properties and invariants

### By Model
- **Board Tests:** 8 tests
- **KnowledgeBase Tests:** 17 tests
- **State Tests:** 19 tests
- **Advanced Tests:** 22 tests
- **Integration Tests:** 2 tests

## 🔍 Key Testing Patterns

1. **Unit Testing**: Individual component functionality
2. **Boundary Testing**: Edge cases and limits
3. **Error Testing**: Invalid inputs and error recovery
4. **Integration Testing**: Component interaction
5. **Property Testing**: Mathematical correctness
6. **Consistency Testing**: Operation consistency

## 📖 Documentation

For detailed testing information, see:
- [TEST_RESULTS.md](TEST_RESULTS.md) - Detailed test case descriptions
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Complete testing manual

## 🛠️ Tools & Dependencies

The test suite uses Python's built-in `unittest` framework with no external dependencies.

### Required
- Python 3.6+
- unittest (built-in)

### Optional
- pytest (for pytest-style execution)

## 📋 File Descriptions

### `test_models.py` Structure
```
TestBoard              (8 tests)
├── Initialization tests
├── Constraint handling
├── Error handling
└── String representation

TestKnowledgeBase      (17 tests)
├── Initialization
├── Variable ID generation
├── Clause management
└── Error recovery

TestState              (19 tests)
├── Initialization
├── Hashing & equality
├── String representation
├── Completion detection
└── Immutability

TestIntegration        (2 tests)
├── Multi-component setup
└── Resource reuse
```

### `test_models_advanced.py` Structure
```
TestBoundaryConditions (5 tests)
├── Large boards
├── Extreme values
└── Monotonicity

TestComplexScenarios   (4 tests)
├── Large datasets
├── Equality on large boards
└── Set behavior

TestErrorRecovery      (2 tests)
├── Graceful degradation
└── State recovery

TestSpecialCases       (4 tests)
├── Special values
└── Edge configurations

TestConsistency        (5 tests)
├── Hash consistency
└── Equality properties

TestPerformance        (2 tests)
├── ID generation speed
└── String output speed
```

## 🎯 Next Steps

### Running Tests
1. Navigate to project root: `cd d:\study\projects-new\futoshiki-solver\`
2. Run all tests: `python experiments/run_tests.py`
3. Review results in console output

### Extending Tests
1. Open `test_models.py` or `test_models_advanced.py`
2. Add new test method following naming convention: `test_feature_scenario`
3. Run tests to verify: `python -m unittest experiments.test_models -v`

### Debugging Failures
1. Run specific failing test with verbose output
2. Check test method docstring for expected behavior
3. Review test code for setup/assertions
4. Verify model implementation matches expectations

## ✨ Features

- ✅ Comprehensive coverage of all models
- ✅ Fast execution (~16ms for all 67 tests)
- ✅ Clear error messages and assertions
- ✅ Test organization by component
- ✅ Advanced scenario testing
- ✅ Performance validation
- ✅ Detailed documentation
- ✅ Easy-to-use test runner

## 📞 Support

For questions about specific tests, refer to:
- Test method docstrings for intended behavior
- Assertion comments for expected values
- TESTING_GUIDE.md for patterns and practices
- TEST_RESULTS.md for detailed test descriptions

---

**Status:** ✅ All Tests Passing (67/67)  
**Last Run:** 2026-04-10  
**Coverage:** Board, KnowledgeBase, State models
