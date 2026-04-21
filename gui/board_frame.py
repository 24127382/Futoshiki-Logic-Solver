"""
Board Frame Module: The 4x4-9x9 Grid Display
=============================================
Renders the Futoshiki grid with:
- Input cells (Entry widgets) for user numbers
- Constraint indicators (< and > signs between cells)
- Dynamic sizing based on puzzle size
"""

import tkinter as tk
from typing import List, Dict, Tuple
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

        self._create_widgets()

    # ========================================================================
    # WIDGET CREATION (FIXED GRID ALIGNMENT)
    # ========================================================================

    def _create_widgets(self) -> None:
        """Create all grid widgets on a single unified grid system."""
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

        self.size = new_size
        self._create_widgets()
