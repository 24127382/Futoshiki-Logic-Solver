"""
DATA FLOW DIAGRAM: Futoshiki Solver Tkinter GUI
===============================================

This document visualizes how data flows through the system.

1. USER INTERACTION FLOW
========================

User clicks "Solve" button
    ↓
Sidebar._on_solve_click()
    ↓ (with size, algorithm, timeout)
App._on_solve_click()
    ↓
Controller.handle_solve_request()
    ↓ (starts background thread)
Controller._solve_worker() [BACKGROUND THREAD]
    ├─ Bridge.ui_to_logic()
    │  └─ Converts GUI strings → InputData
    │
    ├─ Controller._call_solver()
    │  └─ Calls solver.solve(InputData)
    │  └─ Returns OutputData
    │
    ├─ Bridge.logic_to_ui()
    │  └─ Converts OutputData → Dict
    │
    └─ Controller.update_callback()
       └─ Calls _update_ui_from_result() [MAIN THREAD]
          └─ BoardFrame.set_matrix(solution)
          └─ Sidebar.update_stats(stats)
          └─ Sidebar.update_status(message)


2. DATA STRUCTURE TRANSFORMATIONS
==================================

STAGE 1: GUI LAYER
──────────────────
BoardFrame Entry widgets contain:
    entries[0][0].get() → "0"  (string)
    entries[0][1].get() → "2"  (string)
    ...

Sidebar state dict:
    constraint_state = {
        "(0,0)-(0,1)": "<",
        "(0,1)-(1,1)": ">",
    }

       ↓ Bridge.ui_to_logic()

STAGE 2: BRIDGE LAYER
─────────────────────
InputData(
    size=4,
    matrix=[
        [0, 2, 0, 1],   ← Integers, 0 = empty
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ],
    constraints=[
        ((0, 0), (0, 1), '<'),  ← Tuples with signs
        ((0, 1), (1, 1), '>'),
    ]
)

       ↓ Solver.solve(input_data)

STAGE 3: ALGORITHM LAYER
────────────────────────
Solver processes InputData
    ├─ Backtracking: Try numbers 1-4 in each cell
    ├─ Forward Chaining: Propagate constraints
    └─ A*: Use heuristics to search

Returns OutputData:
    OutputData(
        status='success',
        solution=[
            [3, 2, 4, 1],   ← Solved matrix
            [1, 4, 3, 2],
            [4, 1, 2, 3],
            [2, 3, 1, 4]
        ],
        stats={
            'time_ms': 45.2,
            'iterations': 1234,
            'solver': 'Backtracking'
        },
        message='Puzzle solved successfully'
    )

       ↓ Bridge.logic_to_ui()

STAGE 4: BRIDGE LAYER (RETURN)
──────────────────────────────
{
    'status': 'success',
    'solution': [[3,2,4,1], [1,4,3,2], [4,1,2,3], [2,3,1,4]],
    'stats': {'time_ms': 45.2, 'iterations': 1234, 'solver': 'Backtracking'},
    'message': 'Puzzle solved successfully'
}

       ↓ Controller.update_callback()
       ↓ App._update_ui_from_result() [MAIN THREAD]

STAGE 5: GUI LAYER (DISPLAY)
────────────────────────────
BoardFrame.set_matrix(solution)
    └─ entries[0][0].delete(0, END)
       entries[0][0].insert(0, "3")
       entries[0][1].delete(0, END)
       entries[0][1].insert(0, "2")
       ...

Sidebar.update_stats(stats)
    └─ Displays in stats_text widget

GUI shows solved puzzle to user ✓


3. THREADING DIAGRAM
====================

BEFORE:
Time ──→
│
Main Thread: Click Solve → solve() → Display result (BLOCKS 30 SECONDS)
│
└─ GUI FREEZES during solve


AFTER:
Time ──→
│
Main Thread: Click Solve ──┐ → Display result
│                          │
Background Thread: ────────┘→ solve() → callback()
                         (sleeps 30 sec)
│
└─ GUI RESPONSIVE while solving


4. CLASS RELATIONSHIPS
======================

FutoshikiApp (Main Window)
    │
    ├─ owns Sidebar
    │  ├─ on_solve_click → calls App._on_solve_click()
    │  ├─ on_file_load → calls App._on_file_load()
    │  └─ on_size_change → calls App._on_size_change()
    │
    ├─ owns BoardFrame
    │  ├─ get_matrix() → returns GUI data
    │  ├─ get_constraints() → returns constraint state
    │  ├─ set_matrix() → displays solution
    │  └─ set_constraints() → displays constraint signs
    │
    └─ owns FutoshikiController
       ├─ update_callback → calls App._update_ui_from_result()
       ├─ handle_solve_request() → starts background thread
       ├─ _solve_worker() → runs in background
       │  ├─ Bridge.ui_to_logic()
       │  ├─ _call_solver()
       │  └─ Bridge.logic_to_ui()
       │
       └─ owns FutoshikiBridge
          ├─ ui_to_logic() → GUI data → InputData
          └─ logic_to_ui() → OutputData → GUI data


5. ERROR HANDLING FLOW
======================

❌ User clicks SOLVE on empty grid
    └─ Controller validates
       └─ Returns OutputData(status='error', message='Invalid input')
       └─ GUI shows error dialog

❌ Solver timeout (>30 seconds)
    └─ _check_timeout() returns True
    └─ Returns OutputData(status='timeout', message='Timeout after 30s')
    └─ GUI shows "Solving too slow" message

❌ Unsolvable puzzle
    └─ Solver exhausts all possibilities
    └─ Returns OutputData(status='unsolvable', message='No solution found')
    └─ GUI shows "Unsolvable" message

❌ Exception in solver
    └─ try/except in _solve_worker()
    └─ Returns OutputData(status='error', message=str(e))
    └─ GUI shows exception details


6. ASYNC CALLBACK SEQUENCE
==========================

Thread 1 (Main):
    ├─ t=0.0s: User clicks SOLVE
    ├─ t=0.1s: show_solving = True
    ├─ t=0.2s: Spawn Thread 2, return immediately
    └─ Continue handling events...

Thread 2 (Background):
    ├─ t=1.0s: Start solver
    ├─ t=30.0s: Solver finishes
    ├─ t=30.1s: Call update_callback()
    │   └─ self.after(0, _update_ui_from_result, status, data)
    │       (Queue update for main thread)
    └─ Thread exits

Thread 1 (Main):
    ├─ t=30.2s: Event loop processes queued update
    ├─ t=30.3s: _update_ui_from_result() runs
    │   ├─ BoardFrame.set_matrix(solution)
    │   ├─ Sidebar.update_stats(stats)
    │   └─ messagebox.showinfo("Solved!")
    └─ GUI shows result


7. FILE LOADING FLOW
====================

User clicks "Open File"
    ↓
Sidebar._on_file_open()
    ↓
filedialog.askopenfilename()
    ↓ (User selects file)
Sidebar.on_file_load(filepath)
    ↓
App._on_file_load(filepath)
    ↓
Controller.load_puzzle_from_file(filepath)  [TODO: Implement]
    ├─ Parser.parse_file(filepath)
    │  └─ Reads puzzle from .txt file
    │  └─ Returns (matrix, constraints, size)
    │
    ├─ BoardFrame.resize(size)
    ├─ BoardFrame.set_matrix(matrix)
    ├─ BoardFrame.set_constraints(constraints)
    ├─ Sidebar.set_grid_size(size)
    └─ Show "File loaded: puzzle.txt"

Grid now shows loaded puzzle
User can now click SOLVE


8. CONSTRAINT DISPLAY SYSTEM
============================

Constraint Storage Format:
    key = "(row1,col1)-(row2,col2)"
    value = "<" or ">"
    
    Example: "(0,0)-(0,1)" → "<"  means Cell(0,0) < Cell(0,1)

HORIZONTAL constraints (same row):
    Labels appear between cells horizontally
    
    ┌─────┐   ┌─────┐
    │ 1   │ < │ 2   │    ← Label shows "<"
    └─────┘   └─────┘

VERTICAL constraints (same column):
    Labels appear between cells vertically
    
    ┌─────┐
    │ 3   │
    └─────┘
       >        ← Label shows ">"
    ┌─────┐
    │ 1   │
    └─────┘


SUMMARY: THE BIG PICTURE
========================

1. User ─(input)→ GUI (Sidebar, BoardFrame)
2. GUI ─(event)→ App/Controller
3. Controller ─(converts)→ Bridge
4. Bridge ─(InputData)→ Solver
5. Solver ─(OutputData)→ Bridge
6. Bridge ─(converts)→ Controller
7. Controller ─(callback)→ GUI
8. GUI ─(displays)→ User

Each layer is independent:
- UI changes don't affect solvers
- New solvers can be added without UI changes
- Bridge ensures clean data contracts
- Threading keeps UI responsive
"""

if __name__ == "__main__":
    print(__doc__)
