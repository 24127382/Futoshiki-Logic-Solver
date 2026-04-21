"""
Board Frame Module: The 4x4-9x9 Grid Display
=============================================
Renders the Futoshiki grid with:
- Input cells (Entry widgets) for user numbers
- Constraint indicators (< and > signs between cells)
- Dynamic sizing based on puzzle size
- Constraint Mode: Click 2 adjacent cells to create constraints
"""

import tkinter as tk
from tkinter import simpledialog
from typing import List, Dict, Tuple, Optional
import customtkinter as ctk

class BoardFrame(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        size: int = 4,
        cell_width: int = 40,
        constraint_width: int = 30,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.size = size
        self.cell_width = cell_width
        self.constraint_width = constraint_width

        # Storage for widgets
        self.entries: List[List[ctk.CTkEntry]] = []
        self.h_constraints: Dict[Tuple[int, int], ctk.CTkLabel] = {}
        self.v_constraints: Dict[Tuple[int, int], ctk.CTkLabel] = {}

        self.constraint_state: Dict[str, str] = {}
        
        # Constraint Mode state
        self.constraint_mode = False  # Toggle between Value Input and Constraint Mode
        self.selected_cell: Optional[Tuple[int, int]] = None  # First selected cell
        self.cell_bg_original = {}  # Store original cell colors for restore

        self._create_widgets()

    # ========================================================================
    # WIDGET CREATION (FIXED GRID ALIGNMENT)
    # ========================================================================

    def _create_widgets(self) -> None:
        """Create all grid widgets on a single unified grid system."""
        # Instruction panel (shown when in constraint mode)
        self.instruction_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.instruction_frame.pack(padx=10, pady=5)
        
        self.instruction_label = ctk.CTkLabel(
            self.instruction_frame,
            text="",
            text_color="#ffaa00",
            font=("Arial", 10),
            wraplength=300
        )
        self.instruction_label.pack()
        
        # Main container with transparent background to center it nicely
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(padx=10, pady=10, expand=True)

        self.entries = [[None for _ in range(self.size)] for _ in range(self.size)]

        for r in range(self.size):
            for c in range(self.size):
                # 1. Create entry cell
                entry = ctk.CTkEntry(
                    self.grid_frame,
                    width=self.cell_width,
                    height=self.cell_width,
                    font=("Arial", 16, "bold"),
                    justify="center"
                )
                entry.grid(row=r * 2, column=c * 2, padx=2, pady=2)
                self.entries[r][c] = entry
                
                # Bind click event for constraint mode
                entry.bind("<Button-1>", lambda evt, row=r, col=c: self._on_cell_click(row, col))

                # 2. Create horizontal constraint label (Right of the cell)
                if c < self.size - 1:
                    h_constraint = ctk.CTkLabel(
                        self.grid_frame,
                        text="",
                        width=self.constraint_width,
                        text_color="#aaaaaa",
                        font=("Arial", 14, "bold")
                    )
                    h_constraint.grid(row=r * 2, column=c * 2 + 1, padx=0, pady=2)
                    self.h_constraints[(r, c)] = h_constraint

            # 3. Create vertical constraints (Below the row of cells)
            if r < self.size - 1:
                for c in range(self.size):
                    v_constraint = ctk.CTkLabel(
                        self.grid_frame,
                        text="",
                        width=self.cell_width,
                        height=20,
                        text_color="#aaaaaa",
                        font=("Arial", 14, "bold")
                    )
                    v_constraint.grid(row=r * 2 + 1, column=c * 2, padx=2, pady=0)
                    self.v_constraints[(r, c)] = v_constraint

    # ========================================================================
    # DATA GETTERS
    # ========================================================================

    def get_matrix(self) -> List[List[str]]:
        matrix = []
        for r in range(self.size):
            row = []
            for c in range(self.size):
                value = self.entries[r][c].get()
                value = ''.join(ch for ch in value if ch.isdigit())
                row.append(value)
            matrix.append(row)
        return matrix

    def get_constraints(self) -> Dict[str, str]:
        return self.constraint_state.copy()

    def get_size(self) -> int:
        return self.size

    # ========================================================================
    # DATA SETTERS
    # ========================================================================

    def set_matrix(self, matrix: List[List[int]]) -> None:
        if len(matrix) != self.size or len(matrix[0]) != self.size:
            raise ValueError(f"Matrix size {len(matrix)} != board size {self.size}")

        for r in range(self.size):
            for c in range(self.size):
                value = str(matrix[r][c]) if matrix[r][c] != 0 else ""
                self.entries[r][c].delete(0, tk.END)
                self.entries[r][c].insert(0, value)

    def set_constraints(self, constraints: Dict[str, str]) -> None:
        # Clear existing
        for label in self.h_constraints.values(): label.configure(text="")
        for label in self.v_constraints.values(): label.configure(text="")

        # Set new
        for key, sign in constraints.items():
            self._parse_and_display_constraint(key, sign)

        self.constraint_state = constraints.copy()

    def _parse_and_display_constraint(self, key: str, sign: str) -> None:
        try:
            parts = key.split('-')
            if len(parts) != 2: return

            r1, c1 = map(int, parts[0].strip('()').split(','))
            r2, c2 = map(int, parts[1].strip('()').split(','))

            if r1 == r2:  # Horizontal constraint
                label = self.h_constraints.get((r1, min(c1, c2)))
                if label:
                    label.configure(text=sign)
            elif c1 == c2:  # Vertical constraint
                label = self.v_constraints.get((min(r1, r2), c1))
                if label:
                    # UX Fix: Translate < and > to UP/DOWN arrows for vertical readability
                    display_sign = "^" if sign == "<" else "v"
                    label.configure(text=display_sign)
        except (ValueError, IndexError, KeyError):
            pass

    # ========================================================================
    # CONSTRAINT MODE: Interactive Constraint Creation
    # ========================================================================

    def set_constraint_mode(self, enabled: bool) -> None:
        """
        Toggle between Value Input Mode and Constraint Mode.
        
        Args:
            enabled: True for Constraint Mode, False for Value Input Mode
        """
        self.constraint_mode = enabled
        
        # Update instruction label
        if enabled:
            self.instruction_label.configure(
                text="✏️ Constraint Mode Active:\n1. Click a cell (blue highlight)\n2. Click an adjacent cell\n3. Choose < or >",
                text_color="#ffaa00"
            )
        else:
            self.instruction_label.configure(text="")
        
        if not enabled and self.selected_cell:
            self._unhighlight_cell(self.selected_cell)
            self.selected_cell = None

    def _on_cell_click(self, row: int, col: int) -> None:
        """
        Handle cell click. Behavior depends on current mode.
        
        Args:
            row: Row index
            col: Column index
        """
        if not self.constraint_mode:
            return  # In Value Input Mode, normal entry behavior
        
        cell_pos = (row, col)
        
        # If no cell selected yet, select this one
        if self.selected_cell is None:
            self.selected_cell = cell_pos
            self._highlight_cell(cell_pos, "#4a9eff")  # Blue highlight for first cell
            return
        
        # If same cell clicked again, deselect it
        if self.selected_cell == cell_pos:
            self._unhighlight_cell(cell_pos)
            self.selected_cell = None
            return
        
        # Check if adjacent
        if not self._is_adjacent(self.selected_cell, cell_pos):
            # Deselect first cell and select this one
            self._unhighlight_cell(self.selected_cell)
            self.selected_cell = cell_pos
            self._highlight_cell(cell_pos, "#4a9eff")
            return
        
        # Adjacent cell selected - show constraint options
        first = self.selected_cell
        second = cell_pos
        self._show_constraint_dialog(first, second)
        
        # Reset selection
        self._unhighlight_cell(first)
        self.selected_cell = None

    def _is_adjacent(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> bool:
        """
        Check if two cells are adjacent (horizontally or vertically).
        
        Args:
            cell1: (row, col) tuple
            cell2: (row, col) tuple
            
        Returns:
            True if cells are adjacent, False otherwise
        """
        r1, c1 = cell1
        r2, c2 = cell2
        
        # Horizontal adjacency: same row, columns differ by 1
        if r1 == r2 and abs(c1 - c2) == 1:
            return True
        
        # Vertical adjacency: same column, rows differ by 1
        if c1 == c2 and abs(r1 - r2) == 1:
            return True
        
        return False

    def _highlight_cell(self, cell: Tuple[int, int], color: str) -> None:
        """Highlight a cell with a specific color."""
        r, c = cell
        entry = self.entries[r][c]
        entry.configure(border_color=color, border_width=2)
        self.cell_bg_original[cell] = entry.cget("border_color")

    def _unhighlight_cell(self, cell: Tuple[int, int]) -> None:
        """Remove highlight from a cell."""
        r, c = cell
        entry = self.entries[r][c]
        entry.configure(border_width=0)

    def _show_constraint_dialog(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> None:
        """
        Show dialog to select constraint type between two cells.
        
        Args:
            cell1: First cell (row, col)
            cell2: Second cell (row, col)
        """
        r1, c1 = cell1
        r2, c2 = cell2
        
        # Determine constraint direction
        if r1 == r2:  # Horizontal
            if c1 < c2:
                prompt = f"Cell({r1},{c1}) ? Cell({r1},{c2})"
                cell_pair = (cell1, cell2)
            else:
                prompt = f"Cell({r1},{c2}) ? Cell({r1},{c1})"
                cell_pair = (cell2, cell1)
        else:  # Vertical
            if r1 < r2:
                prompt = f"Cell({r1},{c1}) ? Cell({r2},{c1})"
                cell_pair = (cell1, cell2)
            else:
                prompt = f"Cell({r2},{c1}) ? Cell({r1},{c1})"
                cell_pair = (cell2, cell1)
        
        # Create simple dialog with options
        dialog = tk.Toplevel(self)
        dialog.title("Create Constraint")
        dialog.geometry("250x120")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text=prompt, font=("Arial", 11, "bold")).pack(pady=10)
        tk.Label(dialog, text="Select relation:", font=("Arial", 10)).pack()
        
        constraint_sign = tk.StringVar()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def add_constraint(sign):
            self._add_constraint(cell_pair[0], cell_pair[1], sign)
            dialog.destroy()
        
        tk.Button(button_frame, text="  <  ", width=5, 
                 command=lambda: add_constraint("<")).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="  >  ", width=5,
                 command=lambda: add_constraint(">")).pack(side=tk.LEFT, padx=5)

    def _add_constraint(self, cell1: Tuple[int, int], cell2: Tuple[int, int], sign: str) -> None:
        """
        Add a constraint between two cells.
        
        Args:
            cell1: First cell (row, col)
            cell2: Second cell (row, col)
            sign: '<' or '>'
        """
        r1, c1 = cell1
        r2, c2 = cell2
        
        # Create constraint key: "(r1,c1)-(r2,c2)"
        key = f"({r1},{c1})-({r2},{c2})"
        
        # Store constraint
        self.constraint_state[key] = sign
        
        # Display constraint
        self._parse_and_display_constraint(key, sign)

    # ========================================================================
    # UI INTERACTIONS
    # ========================================================================

    def clear_grid(self) -> None:
        for r in range(self.size):
            for c in range(self.size):
                self.entries[r][c].delete(0, tk.END)
        for label in self.h_constraints.values(): label.configure(text="")
        for label in self.v_constraints.values(): label.configure(text="")
        self.constraint_state.clear()

    def disable_editing(self) -> None:
        for r in range(self.size):
            for c in range(self.size):
                self.entries[r][c].configure(state="disabled")

    def enable_editing(self) -> None:
        for r in range(self.size):
            for c in range(self.size):
                self.entries[r][c].configure(state="normal")

    def resize(self, new_size: int) -> None:
        if not (4 <= new_size <= 9): raise ValueError("Size must be 4-9")
        if new_size == self.size: return

        self.grid_frame.destroy()
        self.entries.clear()
        self.h_constraints.clear()
        self.v_constraints.clear()
        self.cell_bg_original.clear()
        self.selected_cell = None

        self.size = new_size
        self._create_widgets()
