#!/usr/bin/env python
"""Test backward chaining solver integration with GUI."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.bridge import InputData, OutputData
from src.solvers.backward_chaining import BackwardChainingSolver
import threading

def test_backward_chaining_4x4_simple():
    """Test backward chaining on a simple 4x4 puzzle."""
    print("\n" + "=" * 60)
    print("TEST 1: 4x4 Simple Puzzle")
    print("=" * 60)
    
    # Simple 4x4 puzzle with some clues from the input file
    puzzle_matrix = [
        [1, 0, 0, 4],
        [0, 3, 0, 0],
        [0, 0, 4, 0],
        [3, 0, 0, 2],
    ]
    
    # Constraints in format ((r1, c1), (r2, c2), op) - simplified for now
    constraints = []
    
    input_data = InputData(
        size=4,
        matrix=puzzle_matrix,
        constraints=constraints
    )
    
    solver = BackwardChainingSolver(timeout=30.0)
    stop_event = threading.Event()
    
    result = solver.solve(input_data, stop_event)
    
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    print(f"Stats: {result.stats}")
    
    if result.solution:
        print("Solution found:")
        for row in result.solution:
            print(f"  {row}")
    
    # Backward chaining should solve this with or without constraints
    assert result.status in ["success", "unsolvable"], f"Expected success or unsolvable, got {result.status}"
    
    if result.status == "success":
        assert result.solution is not None, "Solution should not be None"
        assert len(result.solution) == 4, "Solution should be 4x4"
    
    print("[PASS]")
    return True

def test_backward_chaining_with_constraints():
    """Test backward chaining with inequality constraints."""
    print("\n" + "=" * 60)
    print("TEST 2: 4x4 Puzzle with Constraints")
    print("=" * 60)
    
    # 4x4 puzzle with clues
    puzzle_matrix = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    
    # Add some constraints: (r1, c1) < (r2, c2)
    constraints = [
        ((0, 0), (0, 1), '<'),  # cell[0,0] < cell[0,1]
        ((1, 0), (1, 1), '<'),  # cell[1,0] < cell[1,1]
    ]
    
    input_data = InputData(
        size=4,
        matrix=puzzle_matrix,
        constraints=constraints
    )
    
    solver = BackwardChainingSolver(timeout=30.0)
    stop_event = threading.Event()
    
    result = solver.solve(input_data, stop_event)
    
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    print(f"Stats: {result.stats}")
    
    if result.solution:
        print("Solution found:")
        for row in result.solution:
            print(f"  {row}")
    
    # May be success or unsolvable depending on constraints
    assert result.status in ["success", "unsolvable"], f"Unexpected status: {result.status}"
    
    print("[PASS]")
    return True

def test_backward_chaining_unsolvable():
    """Test backward chaining detects unsolvable puzzles."""
    print("\n" + "=" * 60)
    print("TEST 3: Unsolvable Puzzle Detection")
    print("=" * 60)
    
    # Create a puzzle that's unsolvable (all cells already filled with duplicates)
    puzzle_matrix = [
        [1, 1, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    
    input_data = InputData(
        size=4,
        matrix=puzzle_matrix,
        constraints=[]
    )
    
    solver = BackwardChainingSolver(timeout=30.0)
    stop_event = threading.Event()
    
    result = solver.solve(input_data, stop_event)
    
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    print(f"Stats: {result.stats}")
    
    assert result.status == "unsolvable", f"Expected unsolvable, got {result.status}"
    
    print("[PASS]")
    return True

def test_backward_chaining_timeout():
    """Test backward chaining handles timeout signal."""
    print("\n" + "=" * 60)
    print("TEST 4: Timeout Handling")
    print("=" * 60)
    
    puzzle_matrix = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    
    input_data = InputData(
        size=4,
        matrix=puzzle_matrix,
        constraints=[]
    )
    
    solver = BackwardChainingSolver(timeout=30.0)
    stop_event = threading.Event()
    stop_event.set()  # Immediately signal timeout
    
    result = solver.solve(input_data, stop_event)
    
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    print(f"Stats: {result.stats}")
    
    assert result.status == "timeout", f"Expected timeout, got {result.status}"
    
    print("[PASS]")
    return True

if __name__ == "__main__":
    try:
        test_backward_chaining_4x4_simple()
        test_backward_chaining_with_constraints()
        test_backward_chaining_unsolvable()
        test_backward_chaining_timeout()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[FAILED] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
