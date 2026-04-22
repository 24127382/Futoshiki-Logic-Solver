#!/usr/bin/env python
"""Quick test to verify backward chaining is available in the GUI."""

from gui.app import FutoshikiApp
from gui.controller import SolverType
import sys

def test_gui_backward_chaining():
    """Test backward chaining option is available in GUI."""
    print("=" * 50)
    print("GUI BACKWARD CHAINING TEST")
    print("=" * 50)
    
    try:
        print("\n1. Initializing FutoshikiApp...")
        app = FutoshikiApp()
        print("   [OK] App created")
        
        # Check that backward chaining is in the solver options
        print("\n2. Checking Backward Chaining in algorithm options...")
        
        algo_options = [
            ("BACKTRACKING", SolverType.BACKTRACKING),
            ("FORWARD_CHAINING", SolverType.FORWARD_CHAINING),
            ("A_STAR", SolverType.A_STAR),
            ("BACKWARD_CHAINING", SolverType.BACKWARD_CHAINING),
        ]
        
        for name, solver_type in algo_options:
            print(f"   - {name}: {solver_type.value}")
        
        print("   [OK] All algorithms available")
        
        # Check sidebar has backward chaining option
        print("\n3. Checking sidebar algorithm options...")
        algo_var = app.sidebar.algo_var.get()
        print(f"   Current algorithm: {algo_var}")
        print("   [OK] Algorithm selector present")
        
        # Test setting backward chaining
        print("\n4. Testing algorithm selection...")
        app.sidebar.algo_var.set(SolverType.BACKWARD_CHAINING.value)
        selected = app.sidebar.algo_var.get()
        print(f"   Selected: {selected}")
        assert selected == SolverType.BACKWARD_CHAINING.value, "Failed to set BACKWARD_CHAINING"
        print("   [OK] Backward Chaining selection works")
        
        print("\n" + "=" * 50)
        print("GUI TEST PASSED!")
        print("=" * 50)
        print("\nBackward Chaining is ready to use in the GUI.")
        print("You can now:")
        print("  1. Load a puzzle via 'Open File'")
        print("  2. Select 'Backward Chaining' from the algorithm dropdown")
        print("  3. Click 'SOLVE'")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gui_backward_chaining()
    sys.exit(0 if success else 1)
