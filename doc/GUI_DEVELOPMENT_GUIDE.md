# Futoshiki Solver - GUI Development Guide

## Overview

This guide explains the Reflex GUI architecture, user flow, and how to develop/extend the GUI for the Futoshiki Solver project.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [File Structure](#file-structure)
3. [State Management](#state-management)
4. [User Flow](#user-flow)
5. [Component Structure](#component-structure)
6. [How to Extend/Modify](#how-to-extendmodify)
7. [Integration Points for Logic Team](#integration-points-for-logic-team)
8. [Styling System](#styling-system)
9. [Common Tasks](#common-tasks)

---

## Architecture Overview

The GUI is built using **Reflex**, a Python-only web framework. Here's the high-level architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    REFLEX APP (gui.py)                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │         COMPONENTS (gui/components/)                    │ │
│  │  • board.py - 20x20 grid rendering                      │ │
│  │  • Custom components for future features               │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           △                                   │
│                           │                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │      STATE (gui/state.py)                              │ │
│  │  • FutoshikiState (rx.State)                            │ │
│  │  • matrix, comparisons, files, solving status          │ │
│  │  • Event handlers and business logic                   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           △                                   │
│                           │                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │   STYLES (gui/styles.py)                               │ │
│  │  • Color palette, spacing, typography                  │ │
│  │  • Component-specific styles                            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           △                                   │
│                           │                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │     BACKEND LOGIC (src/)                               │ │
│  │  • Solvers: forward_chaining, backward_chaining, a_star│ │
│  │  • Models: board, state, kb                            │ │
│  │  • Utils: parser, heuristic                            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
gui/
├── __init__.py                  # Package initialization
├── gui.py                       # MAIN ENTRY POINT - App layout & routing
├── state.py                     # STATE MANAGEMENT - FutoshikiState class
├── styles.py                    # STYLING - Colors, spacing, typography
└── components/
    ├── __init__.py
    └── board.py                 # COMPONENTS - 20x20 grid rendering

rxconfig.py                       # Reflex configuration at project root
```

---

## State Management

### **FutoshikiState Class** (gui/state.py)

The `FutoshikiState` class inherits from `rx.State` and manages:

#### **Data Storage:**
```python
class FutoshikiState(rx.State):
    # Puzzle data
    matrix: List[List[str]]           # 20x20 grid of cell values
    comparisons: Dict[str, str]       # {"(r,c)-(r,c+1)": "<"} constraints
    selected_file: str                # Currently selected puzzle file
    available_files: List[str]        # Scanned from inputs/
    
    # Solving state
    is_solving: bool                  # True while solver is running
    solution: List[List[str]]         # Solved puzzle
    execution_time: float             # Solving duration in seconds
    status_message: str               # User feedback message
```

#### **Event Handlers (State Methods):**
```python
def load_available_files()            # Scans inputs/ directory
def load_puzzle_from_file(filename)   # Loads puzzle from .txt file
async def solve_puzzle()              # Solves the puzzle (async)
def reset_puzzle()                    # Clears board
def update_cell(row, col, value)      # Updates a cell value
def on_load()                         # Called on app initialization
```

#### **Reactivity:**
- When any state variable changes, Reflex **automatically re-renders** affected components
- Example: `update_cell()` triggers board re-render
- Example: `is_solving = True` disables the Solve button

---

## User Flow

### **1. App Initialization**
```
User opens http://localhost:3000
           ↓
Reflex renders index() component
           ↓
on_load() is called → load_available_files()
           ↓
Sidebar displays dropdown with puzzle files from inputs/
```

### **2. Loading a Puzzle**
```
User clicks "Load" button
           ↓
on_click handler: FutoshikiState.load_puzzle_from_file(selected_file)
           ↓
load_puzzle_from_file():
  1. Reads .txt file from inputs/
  2. Parses matrix and comparisons using src.utils.parser
  3. Updates FutoshikiState.matrix and .comparisons
  4. Re-renders board with new values
           ↓
Board now shows puzzle with constraint symbols (<, >)
           ↓
User can edit cells in the grid
```

### **3. Solving the Puzzle**
```
User clicks "Solve" button
           ↓
on_click handler: FutoshikiState.solve_puzzle()
           ↓
is_solving = True → Solve button becomes disabled/loading
           ↓
solve_puzzle():
  1. Creates board object from matrix + comparisons
  2. Selects appropriate solver
  3. Runs solver algorithm
  4. Measures execution time
  5. Populates solution variable
  6. Updates status_message
           ↓
is_solving = False → Solve button re-enabled
           ↓
solution is displayed (highlighted differently)
execution_time shows in sidebar and footer
status_message shows success/error
```

### **4. Resetting**
```
User clicks "Reset" button
           ↓
on_click handler: FutoshikiState.reset_puzzle()
           ↓
All state variables reset to initial/empty state
           ↓
Board re-renders as empty
```

---

## Component Structure

### **Core Components**

#### **1. index()** (gui/gui.py)
Main layout component. Returns:
```
hstack:
  ├── sidebar()           # Left panel
  └── vstack:
      ├── header()        # Top title
      ├── render_board()  # Middle (scrollable)
      └── control_bar()   # Bottom (Solve button, stats)
```

#### **2. sidebar()** (gui/gui.py)
Left panel for puzzle management:
- File dropdown
- Load button
- Reset button
- Info display (current file, execution time)
- Status message

#### **3. control_bar()** (gui/gui.py)
Bottom control area:
- **Solve button** - Primary action
- **Execution time** - Shows solver performance
- **Status display** - User feedback

#### **4. render_board()** (gui/components/board.py)
The 20x20 puzzle grid:
```
vstack (all rows):
  └── For each row (0-19):
      ├── hstack (cells + horizontal comparisons):
      │   ├── render_cell(row, 0)
      │   ├── render_horizontal_comparison(row, 0)
      │   ├── render_cell(row, 1)
      │   ├── render_horizontal_comparison(row, 1)
      │   └── ...
      └── (vertical comparisons between rows)
```

---

## How to Extend/Modify

### **Adding a New Component**

1. **Create the component file:**
```python
# gui/components/my_component.py
import reflex as rx
from gui.state import FutoshikiState
from gui import styles

def my_component() -> rx.Component:
    """Description of component."""
    return rx.box(
        rx.vstack(
            rx.text("Component content"),
            spacing=styles.GAP_MEDIUM,
        ),
        style={...}
    )
```

2. **Use it in gui.py:**
```python
from gui.components.my_component import my_component

def index() -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.vstack(
            my_component(),  # Add here
            render_board(),
        ),
    )
```

### **Adding a New State Variable**

1. **Define in FutoshikiState:**
```python
class FutoshikiState(rx.State):
    my_new_var: str = "default"
    my_counter: int = 0
```

2. **Create an event handler:**
```python
def update_my_var(self, value: str):
    """Handle my_new_var changes."""
    self.my_new_var = value
```

3. **Bind in components:**
```python
rx.input(
    value=FutoshikiState.my_new_var,
    on_change=FutoshikiState.update_my_var,
)
```

### **Modifying Styling**

All styles are in `gui/styles.py`. To modify:

1. **Change a color:**
```python
COLOR_PRIMARY = "#00d4ff"  # Cyan - change to your color
```

2. **Change a component style:**
```python
BUTTON_STYLE_PRIMARY = {
    "background_color": COLOR_PRIMARY,
    "padding": "0.75em 1.5em",
    # ... modify properties
}
```

3. **Use in components:**
```python
rx.button("Click", style=styles.BUTTON_STYLE_PRIMARY)
```

### **Modifying the Board**

The board rendering is in `gui/components/board.py`:

**To change cell styling:**
```python
def render_cell(row: int, col: int) -> rx.Component:
    return rx.input(
        value=FutoshikiState.matrix[row][col],
        on_change=lambda v: FutoshikiState.update_cell(row, col, v),
        # Modify style here
        style=styles.CELL_STYLE_EMPTY,  # or create custom style
    )
```

**To change comparison rendering:**
```python
def render_horizontal_comparison(row: int, col: int) -> rx.Component:
    # Modify comparison display here
    constraint_key = f"({row},{col})-({row},{col + 1})"
    comparison = FutoshikiState.comparisons.get(constraint_key, "")
    # ... render comparison
```

---

## Integration Points for Logic Team

### **1. Parsing Puzzles**

**File:** `gui/state.py` → `load_puzzle_from_file()`

```python
# TODO: Replace mock with actual parser
# from src.utils.parser import parse_puzzle_file

def load_puzzle_from_file(self, filename: str):
    # Current: mock loading
    # Expected: Call parser
    matrix, comparisons = parse_puzzle_file(str(inputs_dir / filename))
    self.matrix = matrix
    self.comparisons = comparisons
```

### **2. Solving Puzzles**

**File:** `gui/state.py` → `solve_puzzle()`

```python
async def solve_puzzle(self) -> None:
    # Current: 2 second mock
    # Expected: Real solver
    
    # from src.models.board import FutoshikiBoard
    # from src.solvers.forward_chaining import ForwardChainingSolver
    
    board = FutoshikiBoard(self.matrix, self.comparisons)
    solver = ForwardChainingSolver(board)
    
    start_time = time.time()
    self.solution = solver.solve()
    self.execution_time = time.time() - start_time
```

### **3. Adding Solver Selection**

You can add a dropdown to choose solvers:

```python
# Add to FutoshikiState
solver_type: str = "forward_chaining"

# Modify solve_puzzle() to check solver_type
if self.solver_type == "forward_chaining":
    solver = ForwardChainingSolver(board)
elif self.solver_type == "backward_chaining":
    solver = BackwardChainingSolver(board)
elif self.solver_type == "a_star":
    solver = AStarSolver(board)
```

### **4. Validation**

Add validation before solving:

```python
def solve_puzzle(self) -> None:
    # Validate board is not empty
    if all(cell == "" for row in self.matrix for cell in row):
        self.status_message = "Error: No puzzle loaded"
        return
    
    # Validate solution constraints
    # ...
```

---

## Styling System

### **Color Palette**
```python
COLOR_BG_DARK = "#0f1419"          # Background
COLOR_TEXT_PRIMARY = "#f0f4f8"     # Main text
COLOR_PRIMARY = "#00d4ff"          # Cyan (accents, buttons)
COLOR_SECONDARY = "#7c3aed"        # Purple
COLOR_SUCCESS = "#10b981"          # Green (solution)
COLOR_ERROR = "#ef4444"            # Red (errors)
```

### **Spacing** (Reflex numeric units)
```python
GAP_SMALL = "1"      # Space between elements
GAP_MEDIUM = "3"     # Medium gaps
GAP_LARGE = "5"      # Large gaps
```

### **Typography**
```python
FONT_FAMILY = "Courier, monospace"
FONT_SIZE_HEADING = "24px"
FONT_SIZE_BODY = "14px"
FONT_SIZE_SMALL = "12px"
```

### **Grid**
```python
CELL_SIZE = "35px"           # Width/height of each puzzle cell
GRID_COLS = 20               # 20 columns
GRID_SIZE = 20               # 20 rows
```

---

## Common Tasks

### **Task: Change Cell Input Styling**

**File:** `gui/styles.py`

```python
CELL_STYLE_EMPTY = {
    "width": CELL_SIZE,
    "height": CELL_SIZE,
    "background_color": COLOR_BG_CARD,  # Change this
    "border": f"1px solid {COLOR_BORDER}",
    "color": COLOR_TEXT_PRIMARY,
    # ... other properties
}
```

### **Task: Add Difficulty Level Display**

1. Add to state:
```python
class FutoshikiState(rx.State):
    difficulty: str = "Medium"
```

2. Update when loading:
```python
def load_puzzle_from_file(self, filename: str):
    # Parse difficulty from filename or file content
    self.difficulty = extract_difficulty(filename)
```

3. Display in sidebar:
```python
rx.text(f"Difficulty: {FutoshikiState.difficulty}")
```

### **Task: Add Timer During Solve**

1. Modify state:
```python
import asyncio

async def solve_puzzle(self) -> None:
    self.is_solving = True
    start = time.time()
    
    # While solving, update UI
    while self.is_solving:
        elapsed = time.time() - start
        # Update UI with elapsed time
        await asyncio.sleep(0.1)
```

### **Task: Add Save Solution**

1. Add button in control_bar:
```python
rx.button(
    "Save Solution",
    on_click=FutoshikiState.save_solution,
)
```

2. Implement in state:
```python
def save_solution(self):
    if not self.solution:
        self.status_message = "No solution to save"
        return
    
    output_path = Path("outputs") / f"{self.selected_file}_solution.txt"
    # Write self.solution to file
    self.status_message = f"Saved to {output_path}"
```

### **Task: Add Undo/Redo**

1. Track history in state:
```python
class FutoshikiState(rx.State):
    history: List[List[List[str]]] = []
    history_index: int = -1
```

2. Add to update_cell:
```python
def update_cell(self, row: int, col: int, value: str):
    # Save current state to history
    self.history.append([row[:] for row in self.matrix])
    self.history_index += 1
    
    # Update cell
    self.matrix[row][col] = value
```

3. Add buttons:
```python
rx.button("Undo", on_click=FutoshikiState.undo)
rx.button("Redo", on_click=FutoshikiState.redo)
```

---

## Key Reflex Concepts

### **Reactive Binding**
Components automatically update when state changes:
```python
# This updates automatically when FutoshikiState.status_message changes
rx.text(FutoshikiState.status_message)
```

### **Event Handlers**
Methods in FutoshikiState are called from components:
```python
rx.button("Click", on_click=FutoshikiState.my_handler)
```

### **Conditional Rendering**
```python
rx.cond(
    FutoshikiState.is_solving,
    rx.text("Solving..."),
    rx.text("Ready"),
)
```

### **Computed Values**
For derived state, use properties (for simple cases) or computed vars in newer Reflex versions.

### **Props vs Style**
- **Props:** Reflex-specific attributes (spacing, padding as numbers)
- **Style:** CSS properties passed as dict (background_color, border, etc.)

```python
rx.vstack(
    rx.text("Content"),
    spacing="3",  # Reflex prop
    style={
        "background_color": "#fff",  # CSS style
        "padding": "1em",
    }
)
```

---

## Testing the GUI

### **Run the app:**
```bash
reflex run
```

### **Visit:**
```
http://localhost:3000
```

### **Test workflow:**
1. App loads → sidebar shows puzzle files
2. Select file and click Load → board renders
3. Click Solve → shows solving in progress
4. Solution appears with execution time
5. Click Reset → clears board

---

## Troubleshooting

### **"Invalid var passed for prop"**
- **Cause:** Wrong type for spacing/padding
- **Fix:** Use Reflex numeric strings ("1", "2", etc.) for `spacing` parameter
- **Use CSS values** ("1em", "16px") for style dict properties

### **Components not updating**
- **Cause:** State changes not triggering re-render
- **Fix:** Ensure components reference FutoshikiState variables
- **Check:** All event handlers modify state directly

### **Styling not applying**
- **Cause:** CSS properties in style dict
- **Fix:** Use correct CSS property names (snake_case in dicts)
- **Example:** `background_color`, not `backgroundColor`

---

## Next Steps

1. **Logic Team:** Implement `load_puzzle_from_file()` with actual parser
2. **Logic Team:** Implement `solve_puzzle()` with real solvers
3. **UI Team:** Add solver selection dropdown
4. **UI Team:** Add difficulty display
5. **Both:** Test end-to-end workflow with actual puzzles
6. **Both:** Add performance metrics and visualization

---

## Resources

- **Reflex Docs:** https://reflex.dev/docs/
- **Reflex Components:** https://reflex.dev/docs/components/
- **Python Async:** https://docs.python.org/3/library/asyncio.html
- **Project Architecture:** See `doc/TECHNICAL_ARCHITECTURE.md`

