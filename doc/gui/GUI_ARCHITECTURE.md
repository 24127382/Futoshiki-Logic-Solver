# Futoshiki Solver - Tkinter GUI Architecture

## Quick Start

### Launch GUI
```bash
python main.py
```

### Launch CLI (Original Mode)
```bash
python main.py --cli --input inputs/4x4_matrix.txt --solver backtracking
```

## Architecture Overview

### Data Flow (How Everything Connects)

```
┌─────────────────────────────────────────────────────────────────┐
│                         TKINTER GUI                              │
│                       (gui/app.py)                               │
├──────────────────────────────────┬──────────────────────────────┤
│                                  │                               │
│   SIDEBAR (gui/sidebar.py)       │   BOARD FRAME (board_frame)  │
│   ├─ File Loader                │   ├─ Grid 4x4 to 9x9        │
│   ├─ Size Selector              │   ├─ Entry Cells             │
│   ├─ Algorithm Selector          │   └─ Constraint Display      │
│   ├─ Solve Button               │                               │
│   ├─ Status Display             │                               │
│   └─ Stats Display              │                               │
│                                  │                               │
└─────────┬────────────────────────┴──────────────────────────────┘
          │
          │ Calls controller.handle_solve_request()
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CONTROLLER (gui/controller.py)                 │
│                   (Communication Hub)                            │
│                                                                   │
│  1. Validates input                                              │
│  2. Converts GUI data via Bridge                                │
│  3. Calls solver in background thread                           │
│  4. Handles timeout & errors                                    │
│  5. Converts result back via Bridge                             │
│  6. Updates GUI via callback                                    │
└──────────────┬──────────────────────────────────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
   ┌────────────┐  ┌─────────────────────┐
   │ BRIDGE     │  │ SOLVER ALGORITHMS    │
   │(bridge.py)│  │ (src/solvers/)        │
   │           │  │                       │
   │ Translates│  │ ├─ Backtracking      │
   │ UI ↔ Logic│  │ ├─ Forward Chaining  │
   │           │  │ └─ A*                │
   │ InputData │  │                       │
   │ OutputData│  └─────────────────────┘
   └────────────┘
```

## File Structure

```
gui/
├── app.py              # Main tkinter window
├── controller.py       # Event handler, solver coordinator
├── bridge.py           # Data translator (UI ↔ Logic)
├── board_frame.py      # 4x4-9x9 grid display
├── sidebar.py          # Control panel (left side)
└── __init__.py

src/                    # Logic layer (unchanged)
├── solvers/           # Algorithm implementations
├── models/            # Board, State classes
├── logic/             # Axioms, grounding, reasoning
└── utils/             # Parser, heuristics

main.py                # Entry point (GUI or CLI)
SOLVER_INTEGRATION_GUIDE.py  # How to adapt solvers
```

## Key Concepts

### 1. Bridge Pattern (Data Translation)

**Problem:** GUI uses strings ("1", "2"), solvers need integers (1, 2).
GUI stores constraints as dicts, solvers need tuples.

**Solution:** Bridge class in `gui/bridge.py`

```python
# GUI sends strings
gui_matrix = [["0", "0", "1"], ["2", "0", "0"], ["0", "0", "3"]]
gui_constraints = {"(0,0)-(0,1)": "<", "(0,1)-(1,1)": ">"}

# Bridge converts to solver format
input_data = bridge.ui_to_logic(gui_matrix, gui_constraints, size=3)
# → InputData(size=3, matrix=[[0,0,1],[2,0,0],[0,0,3]], constraints=[((0,0),(0,1),"<"), ...])

# Solver processes
output_data = solver.solve(input_data)

# Bridge converts back to GUI format
result_dict = bridge.logic_to_ui(output_data)
# → {'status': 'success', 'solution': [[...]], 'stats': {...}}

# GUI displays result
board_frame.set_matrix(result_dict['solution'])
```

### 2. MVC Pattern

- **Model:** Board, State classes in `src/models/`
- **View:** Tkinter components (Sidebar, BoardFrame, App)
- **Controller:** `gui/controller.py` - handles events, coordinates data flow

### 3. Async/Threading

GUI remains responsive by running solver in background thread:

```
Main Thread (UI):               Background Thread (Solver):
├─ User clicks "Solve"          ├─ Converts data (Bridge)
├─ Calls controller.handle_solve├─ Calls solver.solve()
├─ Returns immediately          ├─ Sleeps for 30 seconds...
├─ Displays "Solving..."        ├─ Returns solution
├─ Waits for update_callback()  └─ Calls controller callback
│
└─ update_callback() called ◄────┘
   └─ Updates GUI with result
```

## How to Run Tests

### Test Bridge Translation
```python
from gui.bridge import FutoshikiBridge, InputData

bridge = FutoshikiBridge()
gui_matrix = [["0", "0", "1"], ["0", "0", "0"], ["0", "0", "0"]]
input_data = bridge.ui_to_logic(gui_matrix, {}, size=3)
print(input_data)  # InputData object
```

### Test Controller
```python
from gui.controller import FutoshikiController, SolverType

def my_callback(status, data):
    print(f"Status: {status}")
    print(f"Data: {data}")

controller = FutoshikiController(update_callback=my_callback)
controller.handle_solve_request(matrix, constraints, size=4, algorithm=SolverType.BACKTRACKING)
# Solver runs in background, calls my_callback when done
```

### Test BoardFrame
```python
import tkinter as tk
from gui.board_frame import BoardFrame

root = tk.Tk()
board = BoardFrame(root, size=4)
board.pack()

# Set some values
board.set_matrix([[1,2,3,4], [3,4,1,2], [2,3,4,1], [4,1,2,3]])

# Get user input
matrix = board.get_matrix()
print(matrix)
```

## TODO: Implementation Checklist

### Phase 1: Solver Integration (URGENT)
- [ ] Update `src/solvers/backtracking.py` to accept `InputData`, return `OutputData`
- [ ] Update `src/solvers/forward_chaining.py` similarly
- [ ] Update `src/solvers/a_star.py` similarly
- [ ] Implement `controller._call_solver()` to dispatch to correct solver

### Phase 2: File Loading
- [ ] Implement `controller.load_puzzle_from_file()` using `src/utils/parser.py`
- [ ] Wire `sidebar._on_file_load()` to load and display puzzle
- [ ] Support .txt file format

### Phase 3: Polish
- [ ] Add constraint editing (currently display-only)
- [ ] Add loading spinner/overlay while solving
- [ ] Add keyboard shortcuts (Ctrl+O = Open, Enter = Solve)
- [ ] Add puzzle export (save solved puzzle as .txt)

### Phase 4: Testing
- [ ] Unit tests for Bridge
- [ ] Unit tests for Controller
- [ ] Integration tests with solvers
- [ ] UI responsiveness tests with large puzzles

## Debugging Tips

### Controller Debug Info
```python
controller.get_debug_info()
# Returns: {'status': '...', 'is_solving': False, 'last_result': {...}, ...}
```

### Check Thread Status
```python
if controller.is_solving:
    print("Solver still running")
    print(f"Thread alive: {controller.solver_thread.is_alive()}")
```

### Enable Verbose Logging
```python
from gui.bridge import FutoshikiBridge
bridge = FutoshikiBridge()
# Add print statements in bridge.ui_to_logic() and bridge.logic_to_ui()
```

## Architecture Decisions

### Why Bridge Pattern?
- **Decouples UI from Logic:** UI can change without affecting solvers
- **Flexible Data Flow:** Easy to add new data formats or validation
- **Testability:** Can test translation without GUI or solvers

### Why Threading?
- **UI Responsiveness:** Solver doesn't block button clicks
- **Better UX:** Can show "Solving..." spinner while waiting
- **Cancellation:** Can add Cancel button later

### Why Tkinter instead of Reflex?
- **Lightweight:** No web browser needed
- **Direct Control:** Full control over UI layout and behavior
- **No Build Step:** Runs directly without compilation
- **Familiar:** Standard Python GUI library

## Common Issues

### "Module not found: src.solvers"
→ Ensure `sys.path` includes src/ (done in bridge.py and controller.py)

### "GUI freezes while solving"
→ Ensure solver runs in background thread (done in controller._solve_worker())

### "Constraint display shows nothing"
→ Check constraint key format: must be "(r,c)-(r,c)"

### "Size change doesn't resize grid"
→ BoardFrame.resize() implementation (should work, check for errors)

## Next Steps

1. **Update solvers** to accept InputData/return OutputData
2. **Implement _call_solver()** in controller.py
3. **Test end-to-end:** Load file → Solve → Display
4. **Optimize:** Profile for performance bottlenecks
5. **Deploy:** Package as executable (.exe on Windows)
