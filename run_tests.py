#!/usr/bin/env python3
"""Test runner for Eagle platform."""

import unittest
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_tests():
    """Run all Eagle tests."""
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Configure test runner
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True,  # Capture stdout/stderr during test runs
        failfast=False  # Continue running tests after failures
    )
    
    # Run tests
    print("=" * 70)
    print("Running Eagle Test Suite")
    print("=" * 70)
    
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

def run_specific_test(test_module):
    """Run a specific test module."""
    
    try:
        # Import the test module
        if test_module.startswith('test_'):
            module_name = f"tests.{test_module[:-3]}"  # Remove .py extension
        else:
            module_name = f"tests.test_{test_module}"
        
        suite = unittest.TestLoader().loadTestsFromName(module_name)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
        
    except ImportError as e:
        print(f"Error: Could not import test module '{test_module}': {e}")
        return 1

def main():
    """Main entry point for test runner."""
    
    if len(sys.argv) > 1:
        # Run specific test
        test_module = sys.argv[1]
        return run_specific_test(test_module)
    else:
        # Run all tests
        return run_tests()

if __name__ == '__main__':
    sys.exit(main())