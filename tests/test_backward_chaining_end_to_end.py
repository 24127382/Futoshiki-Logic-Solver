#!/usr/bin/env python
"""End-to-end test of backward chaining integration."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.controller import FutoshikiController, SolverType
import threading
import time

def test_backward_chaining_end_to_end():
    """Test solving a puzzle using backward chaining through the controller."""
    print("\n" + "=" * 70)
    print("END-TO-END BACKWARD CHAINING TEST")
    print("=" * 70)
    
    # Setup callback to capture results
    results = {'status': None, 'data': None}
    def on_update(status, data):
        results['status'] = status
        results['data'] = data
        print(f"\n  [Callback] Status: {status}")
        if data:
            print(f"  [Callback] Data: {data}")
        if status == 'success':
            print(f"  [Callback] Solution found!")
            if isinstance(data, dict) and 'solution' in data:
                print(f"  [Callback] First row of solution: {data['solution'][0]}")
    
    # Create controller with callback
    controller = FutoshikiController(update_callback=on_update)
    
    # Test case 1: Simple 4x4 puzzle
    print("\nTest 1: Solving 4x4 puzzle with Backward Chaining")
    print("-" * 70)
    
    gui_matrix = [
        ['1', '', '', '4'],
        ['', '3', '', ''],
        ['', '', '4', ''],
        ['3', '', '', '2'],
    ]
    
    gui_constraints = {}  # No constraints for simplicity
    
    print(f"  Puzzle size: 4x4")
    print(f"  Algorithm: Backward Chaining (DPLL)")
    print(f"  Starting solve...")
    
    controller.handle_solve_request(gui_matrix, gui_constraints, 4, SolverType.BACKWARD_CHAINING)
    
    # Wait for solution
    time.sleep(3)
    
    if results['status'] == 'success':
        print(f"  [SUCCESS] Puzzle solved!")
        solution = results['data']['solution']
        print("  Solution:")
        for row in solution:
            print(f"    {row}")
        return True
    else:
        print(f"  [FAILED] Status: {results['status']}")
        print(f"  [FAILED] Data: {results['data']}")
        return False

def test_backward_chaining_no_clues():
    """Test backward chaining on completely empty puzzle."""
    print("\n" + "=" * 70)
    print("TEST 2: Empty 4x4 Puzzle")
    print("=" * 70)
    
    results = {'status': None, 'data': None}
    
    def on_update(status, data):
        results['status'] = status
        results['data'] = data
    
    controller = FutoshikiController(update_callback=on_update)
    
    gui_matrix = [
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
    ]
    
    print("  Solving completely empty 4x4 puzzle...")
    controller.handle_solve_request(gui_matrix, {}, 4, SolverType.BACKWARD_CHAINING)
    
    time.sleep(3)
    
    if results['status'] in ['success', 'unsolvable']:
        print(f"  [OK] Solver completed with status: {results['status']}")
        return True
    else:
        print(f"  [FAILED] Unexpected status: {results['status']}")
        print(f"  [FAILED] Data: {results['data']}")
        return False

def test_backward_chaining_vs_other_algorithms():
    """Compare backward chaining with other algorithms."""
    print("\n" + "=" * 70)
    print("TEST 3: Algorithm Comparison")
    print("=" * 70)
    
    gui_matrix = [
        ['1', '', '', '4'],
        ['', '3', '', ''],
        ['', '', '4', ''],
        ['3', '', '', '2'],
    ]
    
    algorithms = [
        SolverType.BACKTRACKING,
        SolverType.FORWARD_CHAINING,
        SolverType.A_STAR,
        SolverType.BACKWARD_CHAINING,
    ]
    
    results_data = {}
    
    for algo in algorithms:
        print(f"\n  Testing {algo.name}...")
        
        results = {'status': None, 'time': None}
        
        def on_update(status, data):
            results['status'] = status
            if isinstance(data, dict) and 'stats' in data:
                results['time'] = data['stats'].get('time_ms', 'N/A')
        
        controller = FutoshikiController(update_callback=on_update)
        
        import time as time_module
        start = time_module.time()
        controller.handle_solve_request(gui_matrix, {}, 4, algo)
        time_module.sleep(2)
        elapsed = (time_module.time() - start) * 1000
        
        results_data[algo.name] = {
            'status': results['status'],
            'time_ms': results['time']
        }
        
        print(f"    Status: {results['status']}")
        if results['time']:
            print(f"    Time: {results['time']}ms")
    
    print("\n  Summary:")
    print("  " + "-" * 60)
    for algo_name, result in results_data.items():
        print(f"    {algo_name:20} -> {result['status']:15} ({result['time_ms']}ms)")
    
    # Check that backward chaining succeeded
    bc_result = results_data.get('BACKWARD_CHAINING')
    if bc_result and bc_result['status'] == 'success':
        print("\n  [OK] Backward Chaining working!")
        return True
    else:
        print("\n  [FAILED] Backward Chaining did not succeed")
        return False

if __name__ == "__main__":
    try:
        success = True
        success = test_backward_chaining_end_to_end() and success
        success = test_backward_chaining_no_clues() and success
        success = test_backward_chaining_vs_other_algorithms() and success
        
        print("\n" + "=" * 70)
        if success:
            print("✓ ALL TESTS PASSED!")
            print("=" * 70)
            print("\nBackward Chaining is fully integrated and working!")
            sys.exit(0)
        else:
            print("✗ SOME TESTS FAILED")
            print("=" * 70)
            sys.exit(1)
            
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
