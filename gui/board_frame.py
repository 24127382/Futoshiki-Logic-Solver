"""
Board Frame Module: The 4x4-9x9 Grid Display
=============================================
Renders the Futoshiki grid with:
- Input cells (Entry widgets) for user numbers
- Constraint indicators (< and > signs between cells)
- Dynamic sizing based on puzzle size

Architecture:
- Main grid: TkFrame with dynamic row/column layout
- Cells: CTk.Entry widgets for numbers (1-9)
- Constraints: CTk.Label widgets for < and > signs
- Data access: get_matrix() and get_constraints() for Controller
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Tuple, Optional
import customtkinter as ctk


class BoardFrame(ctk.CTkFrame):
    """
    The 20x20 (or 4x9) puzzle grid UI component.
    
    Structure:
    - self.entries[r][c]: CTkEntry widget for cell (r, c)
    - self.h_constraints[(r,c)]: Label for horizontal < >
    - self.v_constraints[(r,c)]: Label for vertical < >
    
    Responsibility:
    - Display the grid clearly
    - Collect user input from Entry widgets
    - Show constraint signs
    - Allow editing constraints via dropdown or buttons
    """

    def __init__(
        self,
        parent,
        size: int = 4,
        cell_width: int = 40,
        constraint_width: int = 30,
        **kwargs
    ):
        """
        Initialize the board frame.
        
        Args:
            parent: Parent tkinter widget
            size: Grid size (4-9, default 4)
            cell_width: Width of each cell in pixels
            constraint_width: Width of constraint indicators
            **kwargs: Passed to CTkFrame
        """
        super().__init__(parent, **kwargs)
        
        self.size = size
        self.cell_width = cell_width
        self.constraint_width = constraint_width
        
        # Storage for widgets
        self.entries: List[List[ctk.CTkEntry]] = []  # [row][col]
        self.h_constraints: Dict[Tuple[int, int], ctk.CTkLabel] = {}  # (r,c) -> label
        self.v_constraints: Dict[Tuple[int, int], ctk.CTkLabel] = {}  # (r,c) -> label
        
        # Constraint state (will be populated if editing is enabled)
        self.constraint_state: Dict[str, str] = {}  # "(r,c)-(r,c)" -> "<" or ">"
        
        # Build the grid
        self._create_widgets()

    # ========================================================================
    # WIDGET CREATION
    # ========================================================================

    def _create_widgets(self) -> None:
        """Create all grid widgets based on size."""
        # Create main container with grid
        self.grid_frame = ctk.CTkFrame(self)
        self.grid_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Create entries and constraint labels
        self.entries = [[None for _ in range(self.size)] for _ in range(self.size)]
        
        # Layout:
        # Row structure: CELL HCONSTRAINT CELL HCONSTRAINT ... CELL
        # Between rows: vertical constraints
        
        for r in range(self.size):
            # Create row of cells with horizontal constraints
            row_frame = ctk.CTkFrame(self.grid_frame)
            row_frame.grid(row=r * 2, column=0, sticky="ew", padx=2, pady=2)
            
            for c in range(self.size):
                # Create entry cell
                entry = ctk.CTkEntry(
                    row_frame,
                    width=self.cell_width,
                    height=self.cell_width,
                    font=("Arial", 14, "bold"),
                    justify="center"
                )
                entry.grid(row=0, column=c * 2, padx=2, pady=2)
                self.entries[r][c] = entry
                
                # Create horizontal constraint label (between cells)
                if c < self.size - 1:
                    h_constraint = ctk.CTkLabel(
                        row_frame,
                        text="",
                        width=self.constraint_width,
                        text_color="gray",
                        font=("Arial", 12, "bold")
                    )
                    h_constraint.grid(row=0, column=c * 2 + 1, padx=0, pady=2)
                    self.h_constraints[(r, c)] = h_constraint
            
            # Create vertical constraints (between rows)
            if r < self.size - 1:
                v_row_frame = ctk.CTkFrame(self.grid_frame)
                v_row_frame.grid(row=r * 2 + 1, column=0, sticky="ew", padx=2, pady=0)
                
                for c in range(self.size):
                    v_constraint = ctk.CTkLabel(
                        v_row_frame,
                        text="",
                        width=self.cell_width,
                        height=20,
                        text_color="gray",
                        font=("Arial", 12, "bold")
                    )
                    v_constraint.grid(row=0, column=c * 2, padx=2, pady=0)
                    self.v_constraints[(r, c)] = v_constraint

    # ========================================================================
    # DATA GETTERS (What Controller reads from GUI)
    # ========================================================================

    def get_matrix(self) -> List[List[str]]:
        """
        Get all cell values from the grid.
        
        Returns:
            2D list of strings ('' for empty, '1'-'9' for filled)
        """
        matrix = []
        for r in range(self.size):
            row = []
            for c in range(self.size):
                value = self.entries[r][c].get()
                # Clean up: remove non-digit characters
                value = ''.join(ch for ch in value if ch.isdigit())
                row.append(value)
            matrix.append(row)
        return matrix

    def get_constraints(self) -> Dict[str, str]:
        """
        Get all constraints from the board.
        
        Returns:
            Dict mapping constraint keys to signs.
            Example: {'(0,0)-(0,1)': '<', '(0,1)-(1,1)': '>'}
        
        NOTE: Currently returns internal state.
        If editing constraints via UI, this would be populated
        during constraint edit interactions.
        """
        return self.constraint_state.copy()

    def get_size(self) -> int:
        """Get current grid size."""
        return self.size

    # ========================================================================
    # DATA SETTERS (What Controller sends back to GUI)
    # ========================================================================

    def set_matrix(self, matrix: List[List[int]]) -> None:
        """
        Set all cell values in the grid.
        Used to display the solved puzzle.
        
        Args:
            matrix: 2D list of integers
        """
        if len(matrix) != self.size or len(matrix[0]) != self.size:
            raise ValueError(f"Matrix size {len(matrix)} != board size {self.size}")
        
        for r in range(self.size):
            for c in range(self.size):
                value = str(matrix[r][c]) if matrix[r][c] != 0 else ""
                self.entries[r][c].delete(0, tk.END)
                self.entries[r][c].insert(0, value)

    def set_constraints(self, constraints: Dict[str, str]) -> None:
        """
        Set constraint indicators on the board.
        
        Args:
            constraints: Dict mapping "(r,c)-(r,c)" to '<' or '>'
        """
        # Clear existing constraints
        for label in self.h_constraints.values():
            label.configure(text="")
        for label in self.v_constraints.values():
            label.configure(text="")
        
        # Set new constraints
        for key, sign in constraints.items():
            self._parse_and_display_constraint(key, sign)
        
        self.constraint_state = constraints.copy()

    def _parse_and_display_constraint(self, key: str, sign: str) -> None:
        """
        Parse a constraint key and display it.
        
        Key format: "(r1,c1)-(r2,c2)"
        
        Args:
            key: Constraint key string
            sign: '<' or '>'
        """
        try:
            # Parse: "(r1,c1)-(r2,c2)"
            parts = key.split('-')
            if len(parts) != 2:
                return
            
            coord1_str = parts[0].strip().strip('()')
            coord2_str = parts[1].strip().strip('()')
            
            r1, c1 = map(int, coord1_str.split(','))
            r2, c2 = map(int, coord2_str.split(','))
            
            # Determine if horizontal or vertical constraint
            if r1 == r2:  # Horizontal
                if c1 < c2:
                    label = self.h_constraints.get((r1, c1))
                else:
                    label = self.h_constraints.get((r1, c2))
                if label:
                    label.configure(text=sign)
            elif c1 == c2:  # Vertical
                if r1 < r2:
                    label = self.v_constraints.get((r1, c1))
                else:
                    label = self.v_constraints.get((r2, c1))
                if label:
                    label.configure(text=sign)
        except (ValueError, IndexError, KeyError):
            pass  # Ignore malformed constraints

    # ========================================================================
    # UI INTERACTIONS
    # ========================================================================

    def clear_grid(self) -> None:
        """Clear all cell values and constraints."""
        for r in range(self.size):
            for c in range(self.size):
                self.entries[r][c].delete(0, tk.END)
        
        for label in self.h_constraints.values():
            label.configure(text="")
        for label in self.v_constraints.values():
            label.configure(text="")
        
        self.constraint_state.clear()

    def disable_editing(self) -> None:
        """Disable all entry fields (after solving)."""
        for r in range(self.size):
            for c in range(self.size):
                self.entries[r][c].configure(state="disabled")

    def enable_editing(self) -> None:
        """Enable all entry fields."""
        for r in range(self.size):
            for c in range(self.size):
                self.entries[r][c].configure(state="normal")

    # ========================================================================
    # RESIZE (Change grid size 4->5->...->9)
    # ========================================================================

    def resize(self, new_size: int) -> None:
        """
        Resize the grid to a new size.
        
        Args:
            new_size: New grid size (4-9)
        
        TODO: Implement smooth resizing
        - Clear existing widgets
        - Update self.size
        - Recreate grid
        - Optionally preserve data if sizes compatible
        """
        if not (4 <= new_size <= 9):
            raise ValueError("Size must be 4-9")
        
        if new_size == self.size:
            return
        
        # Clear old grid
        self.grid_frame.destroy()
        self.entries.clear()
        self.h_constraints.clear()
        self.v_constraints.clear()
        
        # Update size
        self.size = new_size
        
        # Recreate
        self._create_widgets()
