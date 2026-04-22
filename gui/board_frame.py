import tkinter as tk
from tkinter import simpledialog
from typing import List, Dict, Tuple, Optional
import customtkinter as ctk

class BoardFrame(ctk.CTkFrame):
    def __init__(self, parent, size: int = 4, cell_width: int = 40, constraint_width: int = 30, **kwargs):
        super().__init__(parent, **kwargs)
        self.size = size
        self.cell_width = cell_width
        self.constraint_width = constraint_width
        self.entries: List[List[ctk.CTkEntry]] = []
        self.h_constraints: Dict[Tuple[int, int], ctk.CTkLabel] = {}
        self.v_constraints: Dict[Tuple[int, int], ctk.CTkLabel] = {}
        self.constraint_state: Dict[str, str] = {}
        self.constraint_mode = False
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.cell_bg_original = {}

        # Absolute centering container
        self.center_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.center_wrapper.place(relx=0.5, rely=0.5, anchor="center")

        self._create_widgets()

    def _create_widgets(self) -> None:
        self.instruction_frame = ctk.CTkFrame(self.center_wrapper, fg_color="transparent")
        self.instruction_frame.pack(padx=10, pady=5)

        self.instruction_label = ctk.CTkLabel(
            self.instruction_frame, text="", text_color="darkorange", font=("Arial", 11, "bold"), wraplength=300
        )
        self.instruction_label.pack()

        self.grid_frame = ctk.CTkFrame(self.center_wrapper, fg_color="transparent")
        self.grid_frame.pack(padx=10, pady=10)

        self.entries = [[None for _ in range(self.size)] for _ in range(self.size)]

        for r in range(self.size):
            for c in range(self.size):
                entry = ctk.CTkEntry(
                    self.grid_frame, width=self.cell_width, height=self.cell_width,
                    font=("Arial", 16, "bold"), justify="center"
                )
                entry.grid(row=r * 2, column=c * 2, padx=2, pady=2)
                self.entries[r][c] = entry
                entry.bind("<Button-1>", lambda evt, row=r, col=c: self._on_cell_click(row, col))

                if c < self.size - 1:
                    h_constraint = ctk.CTkLabel(
                        self.grid_frame, text="", width=self.constraint_width, text_color="#333333", font=("Arial", 14, "bold")
                    )
                    h_constraint.grid(row=r * 2, column=c * 2 + 1, padx=0, pady=2)
                    self.h_constraints[(r, c)] = h_constraint

            if r < self.size - 1:
                for c in range(self.size):
                    v_constraint = ctk.CTkLabel(
                        self.grid_frame, text="", width=self.cell_width, height=20, text_color="#333333", font=("Arial", 14, "bold")
                    )
                    v_constraint.grid(row=r * 2 + 1, column=c * 2, padx=2, pady=0)
                    self.v_constraints[(r, c)] = v_constraint

    def get_matrix(self) -> List[List[str]]:
        return [[''.join(ch for ch in self.entries[r][c].get() if ch.isdigit()) for c in range(self.size)] for r in range(self.size)]

    def get_constraints(self) -> Dict[str, str]: return self.constraint_state.copy()
    def get_size(self) -> int: return self.size

    def set_matrix(self, matrix: List[List[int]]) -> None:
        for r in range(self.size):
            for c in range(self.size):
                self.entries[r][c].delete(0, tk.END)
                self.entries[r][c].insert(0, str(matrix[r][c]) if matrix[r][c] != 0 else "")

    def set_constraints(self, constraints: Dict[str, str]) -> None:
        for label in self.h_constraints.values(): label.configure(text="")
        for label in self.v_constraints.values(): label.configure(text="")
        for key, sign in constraints.items(): self._parse_and_display_constraint(key, sign)
        self.constraint_state = constraints.copy()

    def _parse_and_display_constraint(self, key: str, sign: str) -> None:
        try:
            parts = key.split('-')
            r1, c1 = map(int, parts[0].strip('()').split(','))
            r2, c2 = map(int, parts[1].strip('()').split(','))
            if r1 == r2:
                label = self.h_constraints.get((r1, min(c1, c2)))
                if label: label.configure(text=sign)
            elif c1 == c2:
                label = self.v_constraints.get((min(r1, r2), c1))
                if label: label.configure(text="^" if sign == "<" else "v")
        except: pass

    def set_constraint_mode(self, enabled: bool) -> None:
        self.constraint_mode = enabled
        if enabled:
            self.instruction_label.configure(text="Constraint Mode Active: Click a cell, then an adjacent cell.")
        else:
            self.instruction_label.configure(text="")
        if not enabled and self.selected_cell:
            self._unhighlight_cell(self.selected_cell)
            self.selected_cell = None

    def _on_cell_click(self, row: int, col: int) -> None:
        if not self.constraint_mode: return
        cell_pos = (row, col)

        if self.selected_cell is None:
            self.selected_cell = cell_pos
            self._highlight_cell(cell_pos, "#4a9eff")
            return
        if self.selected_cell == cell_pos:
            self._unhighlight_cell(cell_pos)
            self.selected_cell = None
            return
        if not self._is_adjacent(self.selected_cell, cell_pos):
            self._unhighlight_cell(self.selected_cell)
            self.selected_cell = cell_pos
            self._highlight_cell(cell_pos, "#4a9eff")
            return

        self._show_constraint_dialog(self.selected_cell, cell_pos)
        self._unhighlight_cell(self.selected_cell)
        self.selected_cell = None

    def _is_adjacent(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> bool:
        r1, c1, r2, c2 = cell1[0], cell1[1], cell2[0], cell2[1]
        return (r1 == r2 and abs(c1 - c2) == 1) or (c1 == c2 and abs(r1 - r2) == 1)

    def _highlight_cell(self, cell: Tuple[int, int], color: str) -> None:
        self.entries[cell[0]][cell[1]].configure(border_color=color, border_width=2)

    def _unhighlight_cell(self, cell: Tuple[int, int]) -> None:
        self.entries[cell[0]][cell[1]].configure(border_width=0)

    def _show_constraint_dialog(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> None:
        r1, c1, r2, c2 = cell1[0], cell1[1], cell2[0], cell2[1]
        if r1 == r2:
            prompt, cell_pair = (f"Cell({r1},{c1}) ? Cell({r1},{c2})", (cell1, cell2)) if c1 < c2 else (f"Cell({r1},{c2}) ? Cell({r1},{c1})", (cell2, cell1))
        else:
            prompt, cell_pair = (f"Cell({r1},{c1}) ? Cell({r2},{c1})", (cell1, cell2)) if r1 < r2 else (f"Cell({r2},{c1}) ? Cell({r1},{c1})", (cell2, cell1))

        dialog = tk.Toplevel(self)
        dialog.title("Create Constraint")
        dialog.geometry("250x120")
        tk.Label(dialog, text=prompt, font=("Arial", 11, "bold")).pack(pady=10)

        button_frame = tk.Frame(dialog)
        button_frame.pack()
        tk.Button(button_frame, text="  <  ", command=lambda: [self._add_constraint(*cell_pair, "<"), dialog.destroy()]).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="  >  ", command=lambda: [self._add_constraint(*cell_pair, ">"), dialog.destroy()]).pack(side=tk.LEFT, padx=5)

    def _add_constraint(self, cell1: Tuple[int, int], cell2: Tuple[int, int], sign: str) -> None:
        key = f"({cell1[0]},{cell1[1]})-({cell2[0]},{cell2[1]})"
        self.constraint_state[key] = sign
        self._parse_and_display_constraint(key, sign)

    def clear_grid(self) -> None:
        for r in range(self.size):
            for c in range(self.size): self.entries[r][c].delete(0, tk.END)
        for label in self.h_constraints.values(): label.configure(text="")
        for label in self.v_constraints.values(): label.configure(text="")
        self.constraint_state.clear()

    def disable_editing(self) -> None:
        for row in self.entries:
            for entry in row: entry.configure(state="disabled")

    def enable_editing(self) -> None:
        for row in self.entries:
            for entry in row: entry.configure(state="normal")

    def resize(self, new_size: int) -> None:
        if new_size == self.size: return
        self.instruction_frame.destroy()
        self.grid_frame.destroy()
        self.entries.clear()
        self.h_constraints.clear()
        self.v_constraints.clear()
        self.cell_bg_original.clear()
        self.selected_cell = None
        self.size = new_size
        self._create_widgets()
