#!/usr/bin/env python3
"""Test runner for Futoshiki solver unit tests.

Runs all unit tests with comprehensive reporting and summary statistics.
"""

import sys
import os
import unittest
import time
from io import StringIO

# Add parent directory to path so we can import experiments module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """Run all unit tests and provide comprehensive report."""
    
    print("=" * 80)
    print("FUTOSHIKI SOLVER - COMPREHENSIVE UNIT TEST SUITE")
    print("=" * 80)
    print()
    
    # Create test loader
    loader = unittest.TestLoader()
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Load basic tests
    print("Loading test modules...")
    try:
        from tests import test_models
        basic_tests = loader.loadTestsFromModule(test_models)
        suite.addTests(basic_tests)
        print(f"  ✓ test_models.py ({len(basic_tests._tests)} tests)")
    except Exception as e:
        print(f"  ✗ Failed to load test_models: {e}")
        return False
    
    # Load advanced tests
    try:
        from tests import test_models_advanced
        advanced_tests = loader.loadTestsFromModule(test_models_advanced)
        suite.addTests(advanced_tests)
        print(f"  ✓ test_models_advanced.py ({len(advanced_tests._tests)} tests)")
    except Exception as e:
        print(f"  ✗ Failed to load test_models_advanced: {e}")
        return False
    
    print()
    print("=" * 80)
    print("RUNNING TESTS")
    print("=" * 80)
    print()
    
    # Run tests with timing
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    elapsed_time = time.time() - start_time
    
    # Print summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total_tests - failures - errors - skipped
    
    print(f"Total Tests:     {total_tests}")
    print(f"Passed:          {passed} ✓")
    print(f"Failed:          {failures} ✗")
    print(f"Errors:          {errors} ✗")
    print(f"Skipped:         {skipped}")
    print(f"Execution Time:  {elapsed_time:.4f} seconds")
    print()
    
    # Success rate
    if total_tests > 0:
        success_rate = (passed / total_tests) * 100
        print(f"Success Rate:    {success_rate:.1f}%")
    print()
    
    # Detailed failure information
    if failures > 0:
        print("FAILURES:")
        print("-" * 80)
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)
        print()
    
    if errors > 0:
        print("ERRORS:")
        print("-" * 80)
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)
        print()
    
    print("=" * 80)
    
    # Return success
    return result.wasSuccessful()


def run_specific_test_class(test_module_name, test_class_name=None):
    """Run specific test class or module.
    
    Args:
        test_module_name: Name of test module (e.g., 'test_models')
        test_class_name: Optional specific test class (e.g., 'TestBoard')
    """
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    if test_class_name:
        # Load specific test class
        try:
            if test_module_name == 'basic':
                from tests.test_models import TestBoard, TestKnowledgeBase, TestState, TestIntegration
                class_map = {
                    'TestBoard': TestBoard,
                    'TestKnowledgeBase': TestKnowledgeBase,
                    'TestState': TestState,
                    'TestIntegration': TestIntegration,
                }
            else:
                from tests import test_models_advanced
                class_map = {
                    'TestBoundaryConditions': test_models_advanced.TestBoundaryConditions,
                    'TestComplexScenarios': test_models_advanced.TestComplexScenarios,
                    'TestErrorRecovery': test_models_advanced.TestErrorRecovery,
                    'TestSpecialCases': test_models_advanced.TestSpecialCases,
                    'TestConsistency': test_models_advanced.TestConsistency,
                    'TestPerformance': test_models_advanced.TestPerformance,
                }
            
            test_class = class_map.get(test_class_name)
            if test_class:
                suite.addTests(loader.loadTestsFromTestCase(test_class))
                print(f"Running {test_class_name}...\n")
            else:
                print(f"Test class '{test_class_name}' not found")
                return False
        except Exception as e:
            print(f"Error loading test class: {e}")
            return False
    else:
        # Load entire module
        try:
            if test_module_name == 'basic':
                from tests import test_models
                suite.addTests(loader.loadTestsFromModule(test_models))
                print("Running all basic tests...\n")
            else:
                from tests import test_models_advanced
                suite.addTests(loader.loadTestsFromModule(test_models_advanced))
                print("Running all advanced tests...\n")
        except Exception as e:
            print(f"Error loading test module: {e}")
            return False
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'basic':
            success = run_specific_test_class('basic')
        elif sys.argv[1] == 'advanced':
            success = run_specific_test_class('advanced')
        else:
            # Try to run specific test class
            success = run_specific_test_class('basic', sys.argv[1])
    else:
        # Run all tests
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
