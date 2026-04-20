"""
QUICK START: Futoshiki Solver with Tkinter GUI
===============================================

This is your "copy-paste" guide to get the GUI working.

STEP 1: Install Dependencies
-----------------------------
pip install customtkinter

(CustomTkinter is already listed in requirements.txt)


STEP 2: Launch the GUI
----------------------
python main.py


STEP 3: What You'll See
-----------------------
┌─────────────────────────────────┬──────────────────────────┐
│ SIDEBAR                         │ BOARD FRAME              │
│                                 │                          │
│ 📁 Load Puzzle                  │ Futoshiki Grid           │
│ [Open File]                     │ ┌──┬──┬──┬──┐           │
│ No file loaded                  │ │  │  │  │  │           │
│                                 │ ├──┼──┼──┼──┤           │
│ 🔲 Grid Size                    │ │  │  │  │  │           │
│ ○ 4×4                           │ ├──┼──┼──┼──┤           │
│ ○ 5×5                           │ │  │  │  │  │           │
│ ○ 6×6                           │ ├──┼──┼──┼──┤           │
│ ○ 7×7                           │ │  │  │  │  │           │
│ ○ 8×8                           │ └──┴──┴──┴──┘           │
│ ○ 9×9                           │                          │
│                                 │                          │
│ ⚙️ Algorithm                    │                          │
│ ● Backtracking                  │                          │
│ ○ Forward Chaining              │                          │
│ ○ A*                            │                          │
│                                 │                          │
│ ⏱️ Timeout (seconds)            │                          │
│ [30]                            │                          │
│                                 │                          │
│ ▶ SOLVE                         │                          │
│ 🗑️ Clear Grid                   │                          │
│                                 │                          │
│ 📊 Status                       │                          │
│ Ready                           │                          │
│                                 │                          │
│ 📈 Solver Stats                 │                          │
│ [Empty]                         │                          │
└─────────────────────────────────┴──────────────────────────┘


STEP 4: What Needs to Be Done (Phase 1)
----------------------------------------

⚠️  SOLVER INTEGRATION (REQUIRED BEFORE SOLVING)

The solver code is NOT YET integrated with the GUI. You need to:

1. Open: gui/controller.py
2. Find: _call_solver() method (line ~90)
3. Replace: The TODO placeholder with actual solver calls

Example:
--------
from src.solvers.backtracking import BacktrackingSolver

if algorithm == SolverType.BACKTRACKING:
    solver = BacktrackingSolver(timeout=self.timeout_seconds)
    return solver.solve(input_data)  # ← This must return OutputData


STEP 5: Update Your Solvers
----------------------------

Your solvers currently return: List[List[int]]
They need to return: OutputData (from gui.bridge)

Quick Migration:

FROM:
    def solve(self, board):
        # ... algorithm ...
        return solved_matrix

TO:
    def solve(self, input_data: InputData) -> OutputData:
        # Extract data
        matrix = input_data.matrix
        constraints = input_data.constraints
        size = input_data.size
        
        # ... your algorithm ...
        
        # Return result
        return OutputData(
            status='success',
            solution=solved_matrix,
            stats={'time_ms': elapsed, 'iterations': count},
            message='Solved'
        )

See: SOLVER_INTEGRATION_GUIDE.py for full examples


STEP 6: Test the Integration
-----------------------------

Once solvers are updated, try clicking "Solve":

1. Enter some numbers in cells
2. Click "SOLVE"
3. Wait for result
4. Grid should fill with solution
5. Stats should show in bottom-left

If it doesn't work, check console for errors.


STEP 7: File Loading (Optional)
-------------------------------

To load puzzles from .txt files:

1. Click "Open File" button
2. Select a .txt file from inputs/

This requires implementing:
  - controller.load_puzzle_from_file()
  - app._on_file_load()

See: GUI_ARCHITECTURE.md Phase 2 section


COMMON ERRORS
=============

❌ Error: "solve() takes 1 positional argument but 2 were given"
→ Solver signature mismatch. Update solve(self, input_data: InputData)

❌ Error: "OutputData is not defined"
→ Missing import. Add: from gui.bridge import OutputData

❌ Error: "ModuleNotFoundError: No module named 'src.solvers.backtracking'"
→ sys.path not set. Check bridge.py and controller.py have the sys.path.insert(0, src_path)

❌ GUI freezes when solving
→ Solver is running in main thread. Ensure it uses threading (it should automatically)


DEBUG COMMANDS
==============

# Test Bridge
python -c "
from gui.bridge import FutoshikiBridge, InputData
bridge = FutoshikiBridge()
data = InputData(4, [[0,0,0,1], [0,0,0,0], [0,0,0,0], [0,0,0,0]], [])
print('Bridge test:', data)
"

# Test GUI
python main.py

# Test CLI (original mode)
python main.py --cli --input inputs/4x4_matrix.txt --solver backtracking


DATA SCHEMA CHEAT SHEET
=======================

InputData (what solver receives):
{
    'size': 4,  # Grid size 4-9
    'matrix': [[0,0,0,1], [0,2,0,0], ...],  # 0=empty, 1-9=filled
    'constraints': [
        ((0,0), (0,1), '<'),  # Cell(0,0) < Cell(0,1)
        ((0,1), (1,1), '>'),  # Cell(0,1) > Cell(1,1)
    ]
}

OutputData (what solver returns):
{
    'status': 'success',  # 'success' | 'unsolvable' | 'timeout' | 'error'
    'solution': [[1,2,3,4], [3,4,1,2], ...],  # Solved matrix (if success)
    'stats': {'time_ms': 45.2, 'iterations': 1234},
    'message': 'Puzzle solved successfully'
}


NEXT STEPS (In Order)
====================

1. ✅ Run: python main.py
   → Should show GUI

2. ❌ Click SOLVE
   → Should error (solver not integrated yet)

3. ⚠️ UPDATE SOLVERS
   → Change return type to OutputData
   → Add timeout checking
   → Track iterations

4. ⚙️ IMPLEMENT _call_solver() in controller.py
   → Dispatch to correct solver
   → Handle timeouts

5. ✅ Click SOLVE again
   → Should work!

6. 🎯 OPTIMIZE
   → Profile for bottlenecks
   → Test with large puzzles (7x7, 8x8, 9x9)
   → Add UI enhancements


SUPPORT
=======
See:
- GUI_ARCHITECTURE.md - Full architecture
- SOLVER_INTEGRATION_GUIDE.py - Solver migration guide
- gui/controller.py - Comments on what needs implementing
- gui/bridge.py - Data schema definitions
"""

if __name__ == "__main__":
    print(__doc__)
