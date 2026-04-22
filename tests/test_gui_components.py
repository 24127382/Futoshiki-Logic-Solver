#!/usr/bin/env python
"""Quick test to verify GUI components are working"""

from gui.app import FutoshikiApp
import sys

def test_gui():
    """Test GUI initialization"""
    print("=" * 50)
    print("GUI COMPONENT TEST")
    print("=" * 50)
    
    try:
        print("\n1. Initializing FutoshikiApp...")
        app = FutoshikiApp()
        print("   [OK] App created")
        
        # Test Sidebar components
        print("\n2. Checking Sidebar components...")
        assert app.sidebar is not None, "Sidebar not found"
        print("   [OK] Sidebar exists")
        
        assert hasattr(app.sidebar, 'solve_button'), "Solve button missing"
        print("   [OK] Solve button present")
        
        assert hasattr(app.sidebar, 'clear_button'), "Clear button missing"
        print("   [OK] Clear button present")
        
        assert hasattr(app.sidebar, 'scrollable_frame'), "Scrollable frame missing"
        print("   [OK] Scrollable frame present")
        
        assert hasattr(app.sidebar, 'constraint_mode_var'), "Constraint mode toggle missing"
        print("   [OK] Constraint mode toggle present")
        
        assert hasattr(app.sidebar, 'file_button'), "File button missing"
        print("   [OK] File button present")
        
        # Test Board Frame components
        print("\n3. Checking Board Frame components...")
        assert app.board_frame is not None, "Board frame not found"
        print("   [OK] Board frame exists")
        
        assert hasattr(app.board_frame, 'instruction_label'), "Instruction label missing"
        print("   [OK] Instruction label present")
        
        assert hasattr(app.board_frame, 'constraint_mode'), "Constraint mode state missing"
        print("   [OK] Constraint mode state present")
        
        assert hasattr(app.board_frame, 'entries'), "Entries grid missing"
        assert len(app.board_frame.entries) == 4, "Grid not 4x4"
        print("   [OK] 4x4 Grid initialized")
        
        # Test constraint creation
        print("\n4. Testing Constraint Mode...")
        app.board_frame.set_constraint_mode(True)
        assert app.board_frame.constraint_mode == True, "Constraint mode not enabled"
        print("   [OK] Constraint mode toggled ON")
        
        app.board_frame.set_constraint_mode(False)
        assert app.board_frame.constraint_mode == False, "Constraint mode not disabled"
        print("   [OK] Constraint mode toggled OFF")
        
        # Test data getters
        print("\n5. Testing Data Getters...")
        matrix = app.board_frame.get_matrix()
        assert len(matrix) == 4, "Matrix size incorrect"
        print("   [OK] Matrix getter works")
        
        constraints = app.board_frame.get_constraints()
        assert isinstance(constraints, dict), "Constraints not a dict"
        print("   [OK] Constraints getter works")
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
        print("\nGUI is ready. Run: python main.py")
        return True
        
    except AssertionError as e:
        print(f"\n[FAILED] {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gui()
    sys.exit(0 if success else 1)
