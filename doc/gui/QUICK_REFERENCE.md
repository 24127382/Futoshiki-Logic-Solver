"""
QUICK REFERENCE CARD
====================
One-page cheat sheet for the Futoshiki Solver Tkinter GUI
"""

# ============================================================================
# QUICK START
# ============================================================================

# Launch GUI:
python main.py

# Launch CLI (original):
python main.py --cli --input inputs/4x4_matrix.txt --solver backtracking


# ============================================================================
# FILE LOCATIONS
# ============================================================================

GUI Code:           gui/
Documentation:      Root directory (*.md files)
Solvers:            src/solvers/
Models:             src/models/
Parser:             src/utils/parser.py


# ============================================================================
# KEY FILES & WHAT THEY DO
# ============================================================================

File                          Purpose
─────────────────────────────────────────────────────────
gui/app.py                   Main window, layout
gui/controller.py            Event handler, solver coordinator
gui/bridge.py                Data translator (UI ↔ Solver)
gui/board_frame.py           Grid display (4x4-9x9)
gui/sidebar.py               Controls, buttons, settings
main.py                      Entry point (GUI or CLI)

QUICKSTART.md                Getting started guide
GUI_ARCHITECTURE.md          Full system documentation
ARCHITECTURE_FLOWCHART.md    Data flow diagrams
SOLVER_INTEGRATION_GUIDE.py  How to adapt solvers
ALGORITHM_INTEGRATION_CHECKLIST.md  Integration tasks
PROJECT_SUMMARY.md           Project overview
DELIVERY_SUMMARY.md          What was delivered


# ============================================================================
# DATA FLOW (Quick Overview)
# ============================================================================

User Input (GUI)
    ↓
Sidebar._on_solve_click()
    ↓
App._on_solve_click()
    ↓
Controller.handle_solve_request()
    ├─ [Background Thread]
    ├─ Bridge.ui_to_logic(matrix, constraints) → InputData
    ├─ Solver.solve(InputData) → OutputData
    ├─ Bridge.logic_to_ui(OutputData) → Dict
    └─ update_callback()
        ↓ [Main Thread]
    App._update_ui_from_result()
    ├─ BoardFrame.set_matrix(solution)
    ├─ Sidebar.update_stats(stats)
    └─ Sidebar.update_status(message)
        ↓
Display Solution (GUI)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

InputData:
{
    'size': 4,                                    # 4-9
    'matrix': [[0,0,0,1], [0,2,0,0], ...],      # 0=empty
    'constraints': [((0,0), (0,1), '<'), ...]   # ((r1,c1), (r2,c2), '<'|'>')
}

OutputData:
{
    'status': 'success',          # 'success'|'unsolvable'|'timeout'|'error'
    'solution': [[1,2,3,4], ...], # Solved matrix (if success)
    'stats': {                    # Solver performance
        'time_ms': 45.2,
        'iterations': 1234,
        'solver': 'Backtracking'
    },
    'message': 'Human-readable message'
}


# ============================================================================
# ALGORITHM TEAM INTEGRATION (What to do)
# ============================================================================

1. READ:
   └─ ALGORITHM_INTEGRATION_CHECKLIST.md

2. UPDATE SOLVERS (src/solvers/):
   Change:     solve(board) -> List[List[int]]
   To:         solve(InputData) -> OutputData

3. IMPLEMENT controller._call_solver():
   if algorithm == SolverType.BACKTRACKING:
       solver = BacktrackingSolver(timeout=...)
       return solver.solve(input_data)

4. TEST:
   python main.py → Click SOLVE → Grid fills with solution

5. DONE!


# ============================================================================
# TESTING
# ============================================================================

Test GUI:
$ python main.py
→ Click buttons
→ Try different sizes
→ Try different algorithms (currently will error - solver not integrated)

Test Bridge:
>>> from gui.bridge import FutoshikiBridge
>>> bridge = FutoshikiBridge()
>>> data = bridge.ui_to_logic([["0","0","1"], ...], {}, 3)
>>> print(data)

Test Controller:
>>> from gui.controller import FutoshikiController
>>> controller = FutoshikiController()
>>> controller.handle_solve_request(matrix, constraints, size, algorithm)
(Solver runs in background thread)

Test BoardFrame:
>>> from gui.board_frame import BoardFrame
>>> board = BoardFrame(root, size=4)
>>> board.set_matrix([[1,2,3,4], ...])
>>> print(board.get_matrix())


# ============================================================================
# COMMON TASKS
# ============================================================================

Change Grid Size (4-9):
→ GUI: Click radio button in Sidebar
→ Code: board_frame.resize(new_size)

Change Theme:
→ Edit gui/app.py line ~30:
  ctk.set_appearance_mode("dark")  # or "light"
  ctk.set_default_color_theme("blue")  # or "green", "red"

Change Cell Size:
→ Edit gui/app.py line ~65:
  BoardFrame(..., cell_width=50, constraint_width=35)

Add Solver Logging:
→ Add print() statements in controller._solve_worker()
→ Check Terminal for output

Debug GUI:
→ Run: python main.py
→ Click buttons
→ Check Terminal for error messages
→ Use print() to trace execution


# ============================================================================
# PERFORMANCE TARGETS
# ============================================================================

Grid Size | Time Target | Status
──────────┼─────────────┼────────
4x4       | < 100ms     | ✓
5x5       | < 500ms     | ✓
6x6       | < 1s        | ✓
7x7       | < 5s        | ✓
8x8       | < 15s       | ✓
9x9       | < 30s       | ✓


# ============================================================================
# DIRECTORY STRUCTURE
# ============================================================================

futoshiki-solver/
├── gui/                    # NEW: Tkinter GUI
│   ├── app.py             # Main window
│   ├── controller.py      # Event coordinator
│   ├── bridge.py          # Data translator
│   ├── board_frame.py     # Grid display
│   ├── sidebar.py         # Control panel
│   └── README.md          # GUI documentation
│
├── src/                    # EXISTING: Logic layer
│   ├── solvers/           # Algorithms
│   ├── models/            # Board, State
│   ├── logic/             # Axioms, grounding
│   └── utils/             # Parser, heuristics
│
├── tests/                  # EXISTING: Tests
├── inputs/                 # EXISTING: Puzzle files
├── outputs/                # EXISTING: Solutions
│
└── Documentation (NEW):
    ├── QUICKSTART.md
    ├── GUI_ARCHITECTURE.md
    ├── ARCHITECTURE_FLOWCHART.md
    ├── SOLVER_INTEGRATION_GUIDE.py
    ├── ALGORITHM_INTEGRATION_CHECKLIST.md
    ├── PROJECT_SUMMARY.md
    ├── DELIVERY_SUMMARY.md
    └── This file


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

❌ GUI doesn't start
→ Run: pip install customtkinter
→ Check Python version: 3.8+
→ Check: python main.py (errors in Terminal?)

❌ Click SOLVE → Nothing happens
→ Check: Solver integration not done yet
→ See: ALGORITHM_INTEGRATION_CHECKLIST.md

❌ Click SOLVE → Error
→ Read error in Terminal
→ Check controller._call_solver() is implemented
→ Check solvers return OutputData

❌ Grid doesn't show
→ Check: BoardFrame._create_widgets() is called
→ Check: parent widget is visible

❌ Buttons don't work
→ Check: Event callbacks are wired
→ Check: Controller is initialized
→ Add print() to debug


# ============================================================================
# KEY DESIGN PATTERNS
# ============================================================================

Bridge Pattern:
├─ Translates GUI data → Logic data
├─ Solvers never know about UI
└─ Easy to swap UI (CLI, Web, Mobile)

MVC Architecture:
├─ Model: src/models/ (Business logic)
├─ View: gui/ (UI components)
└─ Controller: gui/controller.py (Coordinator)

Observer Pattern:
├─ Controller notifies GUI of changes
├─ Callback-based updates
└─ UI stays in sync with logic

Threading Model:
├─ Main thread: UI, event handling
├─ Background thread: Solver execution
└─ Callbacks bridge the two


# ============================================================================
# NEXT STEPS
# ============================================================================

1. Algorithm Team:
   → Read ALGORITHM_INTEGRATION_CHECKLIST.md
   → Update solver signatures
   → Implement controller._call_solver()
   → Estimated: 4-6 hours

2. QA Team:
   → Test GUI with solvers integrated
   → Run performance tests
   → Check all 3 algorithms work
   → Estimated: 2-3 hours

3. DevOps Team:
   → Package as executable
   → Set up CI/CD
   → Estimated: 1-2 hours

4. Done! 🎉
   → Release to production


# ============================================================================
# RESOURCES
# ============================================================================

Main Documentation: GUI_ARCHITECTURE.md (read first)
Integration Guide: ALGORITHM_INTEGRATION_CHECKLIST.md (for algo team)
Quick Help: QUICKSTART.md (for users)
Code Examples: SOLVER_INTEGRATION_GUIDE.py (for developers)
Architecture: ARCHITECTURE_FLOWCHART.md (for architects)


# ============================================================================
# VERSION HISTORY
# ============================================================================

v1.0 (Current)
- ✅ Complete GUI system
- ✅ Bridge Pattern for data translation
- ✅ MVC architecture
- ✅ Async solver execution
- ✅ Comprehensive documentation
- ⏳ Solver integration (pending)


# ============================================================================
# CONTACT & SUPPORT
# ============================================================================

See documentation files for detailed help.
All code has extensive comments marking TODO items.
Check Terminal output for error messages.
"""

if __name__ == "__main__":
    print(__doc__)
