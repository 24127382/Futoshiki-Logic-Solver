"""
Board Frame Module: The Futoshiki grid display
================================================
Renders the 4x4 – 9x9 Futoshiki grid with:
- Polished, themed cells (hover + focus ring, error highlighting)
- Clickable constraint slots that toggle between ``<``, ``>`` and ``·`` (none)
- Animated "solved-cell" fill when the solver finishes
- Strict input validation (only 1..N digits allowed)
- Utilities for the controller (get/set matrix, get/set constraints, clear…)

Design goals:
- Every visual token comes from ``gui.theme`` so the look is consistent.
- The frame exposes a small, typed API used by the controller. It does not
  import anything solver-related – that's the controller's job.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Dict, List, Optional, Tuple

import customtkinter as ctk

from gui.theme import Palette, Typography, Spacing, Radii, cell_size_for, constraint_size_for


# Constraint cycle when the user clicks a constraint slot.
# '' -> '<' -> '>' -> ''  (three states)
_CONSTRAINT_CYCLE = {"": "<", "<": ">", ">": ""}


class BoardFrame(ctk.CTkFrame):
    """Interactive Futoshiki board widget."""

    # --------------------------------------------------------------
    # Construction
    # --------------------------------------------------------------

    def __init__(
        self,
        parent,
        size: int = 5,
        editable_constraints: bool = True,
        on_constraint_change: Optional[Callable[[], None]] = None,
        on_cell_change: Optional[Callable[[int, int, str], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            fg_color=Palette.BG_BASE,
            corner_radius=Radii.LG,
            **kwargs,
        )

        self.size: int = size
        self.editable_constraints: bool = editable_constraints
        self.on_constraint_change = on_constraint_change
        self.on_cell_change = on_cell_change

        # Widget registries
        self.entries: List[List[ctk.CTkEntry]] = []
        self.h_constraints: Dict[Tuple[int, int], ctk.CTkLabel] = {}
        self.v_constraints: Dict[Tuple[int, int], ctk.CTkLabel] = {}

        # Constraint state: key "(r1,c1)-(r2,c2)" -> "<" | ">"
        self.constraint_state: Dict[str, str] = {}

        # Track cells that are "locked" (pre-filled from the initial puzzle)
        self._locked_cells: set = set()
        # Track cells that were filled by the solver (for animated highlight)
        self._solved_cells: set = set()
        # Cells currently marked as conflicting
        self._error_cells: set = set()

        # Build the outer chrome and inner grid
        self._build_chrome()
        self._build_grid()

    # --------------------------------------------------------------
    # Layout scaffolding
    # --------------------------------------------------------------

    def _build_chrome(self) -> None:
        """Outer padded container that frames the grid itself."""
        self._outer = ctk.CTkFrame(
            self,
            fg_color=Palette.BG_SURFACE,
            corner_radius=Radii.XL,
            border_width=1,
            border_color=Palette.BORDER,
        )
        self._outer.pack(padx=Spacing.LG, pady=Spacing.LG, fill="both", expand=True)

        # Header strip with grid size hint
        self._header = ctk.CTkFrame(
            self._outer,
            fg_color="transparent",
            height=28,
        )
        self._header.pack(fill="x", padx=Spacing.LG, pady=(Spacing.MD, 0))

        self._size_label = ctk.CTkLabel(
            self._header,
            text=f"Grid  {self.size} × {self.size}",
            font=Typography.small(),
            text_color=Palette.TEXT_SECONDARY,
        )
        self._size_label.pack(side="left")

        self._legend_label = ctk.CTkLabel(
            self._header,
            text="Click ‹ / › slots to toggle constraints",
            font=Typography.small(),
            text_color=Palette.TEXT_MUTED,
        )
        self._legend_label.pack(side="right")

        # Inner grid container (this one is rebuilt on resize)
        self._grid_host = ctk.CTkFrame(
            self._outer,
            fg_color=Palette.BG_ELEVATED,
            corner_radius=Radii.LG,
            border_width=1,
            border_color=Palette.BORDER,
        )
        self._grid_host.pack(padx=Spacing.LG, pady=Spacing.LG)

    def _build_grid(self) -> None:
        """Create all the cells and constraint slots."""
        # Wipe previous children (resize safety)
        for child in self._grid_host.winfo_children():
            child.destroy()

        self.entries = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.h_constraints.clear()
        self.v_constraints.clear()

        cell_px = cell_size_for(self.size)
        gap_px = constraint_size_for(self.size)
        cell_font = Typography.cell(self.size)
        cons_font = Typography.constraint(self.size)

        # Outer pad
        pad = Spacing.MD
        grid_wrapper = ctk.CTkFrame(self._grid_host, fg_color="transparent")
        grid_wrapper.pack(padx=pad, pady=pad)

        # Build a (2N-1) x (2N-1) matrix: cells on even indexes, constraints between
        for r in range(self.size):
            for c in range(self.size):
                # --- Cell ---
                entry = self._make_cell(grid_wrapper, r, c, cell_px, cell_font)
                entry.grid(row=r * 2, column=c * 2, padx=1, pady=1)
                self.entries[r][c] = entry

                # --- Horizontal constraint to the right ---
                if c < self.size - 1:
                    lbl = self._make_constraint_label(
                        grid_wrapper, gap_px, cell_px, cons_font, orientation="h"
                    )
                    lbl.grid(row=r * 2, column=c * 2 + 1, sticky="nsew")
                    self.h_constraints[(r, c)] = lbl
                    self._bind_constraint_click(lbl, r, c, horizontal=True)

            # --- Vertical constraints to the row below ---
            if r < self.size - 1:
                for c in range(self.size):
                    lbl = self._make_constraint_label(
                        grid_wrapper, cell_px, gap_px, cons_font, orientation="v"
                    )
                    lbl.grid(row=r * 2 + 1, column=c * 2, sticky="nsew")
                    self.v_constraints[(r, c)] = lbl
                    self._bind_constraint_click(lbl, r, c, horizontal=False)

        # Update header text
        self._size_label.configure(text=f"Grid  {self.size} × {self.size}")

    # --------------------------------------------------------------
    # Cell factory
    # --------------------------------------------------------------

    def _make_cell(
        self, parent, r: int, c: int, size_px: int, font: tuple
    ) -> ctk.CTkEntry:
        entry = ctk.CTkEntry(
            parent,
            width=size_px,
            height=size_px,
            font=font,
            justify="center",
            fg_color=Palette.BG_INPUT,
            text_color=Palette.CELL_TEXT,
            border_color=Palette.BORDER,
            border_width=1,
            corner_radius=Radii.MD,
        )

        # Keystroke validation: accept at most one digit in [1..N]
        vcmd = (self.register(lambda new_val, R=r, C=c: self._validate_cell_input(new_val, R, C)), "%P")
        entry.configure(validate="key", validatecommand=vcmd)

        # Focus ring + hover effects
        entry.bind("<FocusIn>", lambda e, w=entry: self._on_cell_focus_in(w))
        entry.bind("<FocusOut>", lambda e, w=entry: self._on_cell_focus_out(w))
        entry.bind("<Enter>", lambda e, w=entry: self._on_cell_hover(w, True))
        entry.bind("<Leave>", lambda e, w=entry: self._on_cell_hover(w, False))

        # Arrow-key navigation between cells
        entry.bind("<Up>", lambda e, R=r, C=c: self._focus_cell(R - 1, C))
        entry.bind("<Down>", lambda e, R=r, C=c: self._focus_cell(R + 1, C))
        entry.bind("<Left>", lambda e, R=r, C=c: self._handle_left(R, C, e))
        entry.bind("<Right>", lambda e, R=r, C=c: self._handle_right(R, C, e))
        entry.bind("<Return>", lambda e, R=r, C=c: self._focus_cell(R + 1, C))
        entry.bind("<Tab>", lambda e, R=r, C=c: self._focus_cell(R, C + 1))

        # Notify controller on edit
        entry.bind("<KeyRelease>", lambda e, R=r, C=c: self._notify_cell_change(R, C))

        return entry

    # --------------------------------------------------------------
    # Constraint slot factory
    # --------------------------------------------------------------

    def _make_constraint_label(
        self, parent, width: int, height: int, font: tuple, orientation: str
    ) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(
            parent,
            text="·",
            width=width,
            height=height,
            text_color=Palette.TEXT_MUTED,
            fg_color="transparent",
            font=font,
            corner_radius=Radii.SM,
        )
        return lbl

    def _bind_constraint_click(
        self, lbl: ctk.CTkLabel, r: int, c: int, horizontal: bool
    ) -> None:
        if not self.editable_constraints:
            return
        lbl.configure(cursor="hand2")
        lbl.bind("<Button-1>", lambda e, R=r, C=c, H=horizontal: self._cycle_constraint(R, C, H))
        lbl.bind("<Enter>", lambda e, w=lbl: w.configure(fg_color=Palette.BG_HOVER))
        lbl.bind("<Leave>", lambda e, w=lbl: w.configure(fg_color="transparent"))

    def _cycle_constraint(self, r: int, c: int, horizontal: bool) -> None:
        """Rotate a constraint slot through "" → "<" → ">" → ""."""
        if horizontal:
            key = f"({r},{c})-({r},{c + 1})"
            lbl = self.h_constraints.get((r, c))
        else:
            key = f"({r},{c})-({r + 1},{c})"
            lbl = self.v_constraints.get((r, c))

        if lbl is None:
            return

        current = self.constraint_state.get(key, "")
        nxt = _CONSTRAINT_CYCLE[current]
        if nxt:
            self.constraint_state[key] = nxt
        else:
            self.constraint_state.pop(key, None)

        self._render_constraint(lbl, nxt, horizontal)
        if self.on_constraint_change:
            self.on_constraint_change()

    def _render_constraint(self, lbl: ctk.CTkLabel, sign: str, horizontal: bool) -> None:
        if sign == "":
            lbl.configure(text="·", text_color=Palette.TEXT_MUTED)
            return

        # Map logical sign to the glyph the user actually sees based on orientation.
        if horizontal:
            glyph = "<" if sign == "<" else ">"
        else:
            # Vertical: "<" means top < bottom (use ∧), ">" means top > bottom (∨)
            glyph = "∧" if sign == "<" else "∨"

        lbl.configure(text=glyph, text_color=Palette.ACCENT)

    # --------------------------------------------------------------
    # Validation + hover + focus
    # --------------------------------------------------------------

    def _validate_cell_input(self, new_val: str, r: int, c: int) -> bool:
        if new_val == "":
            return True
        if len(new_val) > 1:
            return False
        if not new_val.isdigit():
            return False
        digit = int(new_val)
        return 1 <= digit <= self.size

    def _on_cell_focus_in(self, widget: ctk.CTkEntry) -> None:
        widget.configure(border_color=Palette.BORDER_FOCUS, border_width=2)

    def _on_cell_focus_out(self, widget: ctk.CTkEntry) -> None:
        # Preserve the locked / solved / error state when we leave focus.
        r, c = self._find_cell(widget)
        if (r, c) in self._error_cells:
            widget.configure(border_color=Palette.ERROR, border_width=2)
        else:
            widget.configure(border_color=Palette.BORDER, border_width=1)

    def _on_cell_hover(self, widget: ctk.CTkEntry, entering: bool) -> None:
        if widget.focus_get() is widget:
            return
        r, c = self._find_cell(widget)
        if (r, c) in self._error_cells:
            return
        if entering:
            widget.configure(border_color=Palette.BORDER_STRONG)
        else:
            widget.configure(border_color=Palette.BORDER)

    # --------------------------------------------------------------
    # Navigation helpers
    # --------------------------------------------------------------

    def _focus_cell(self, r: int, c: int) -> str:
        if 0 <= r < self.size and 0 <= c < self.size:
            self.entries[r][c].focus_set()
            self.entries[r][c].select_range(0, "end")
        return "break"

    def _handle_left(self, r: int, c: int, event) -> str:
        widget = event.widget
        if widget.index("insert") == 0:
            return self._focus_cell(r, c - 1)
        return ""

    def _handle_right(self, r: int, c: int, event) -> str:
        widget = event.widget
        value = widget.get()
        if widget.index("insert") >= len(value):
            return self._focus_cell(r, c + 1)
        return ""

    def _find_cell(self, widget: ctk.CTkEntry) -> Tuple[int, int]:
        for r in range(self.size):
            for c in range(self.size):
                if self.entries[r][c] is widget:
                    return r, c
        return -1, -1

    def _notify_cell_change(self, r: int, c: int) -> None:
        if self.on_cell_change:
            self.on_cell_change(r, c, self.entries[r][c].get())

    # --------------------------------------------------------------
    # Error state (driven by the controller's validator)
    # --------------------------------------------------------------

    def highlight_errors(self, cells: List[Tuple[int, int]]) -> None:
        """Tint the given cells red. Pass an empty list to clear."""
        # Clear old
        for r, c in self._error_cells:
            if 0 <= r < self.size and 0 <= c < self.size:
                entry = self.entries[r][c]
                if (r, c) in self._locked_cells:
                    self._style_locked(entry)
                else:
                    entry.configure(
                        fg_color=Palette.BG_INPUT,
                        border_color=Palette.BORDER,
                        border_width=1,
                        text_color=Palette.CELL_TEXT,
                    )

        self._error_cells = set(cells)
        for r, c in self._error_cells:
            if 0 <= r < self.size and 0 <= c < self.size:
                entry = self.entries[r][c]
                entry.configure(
                    fg_color=Palette.CELL_ERROR,
                    border_color=Palette.ERROR,
                    border_width=2,
                    text_color=Palette.ERROR,
                )

    # --------------------------------------------------------------
    # Cell styling helpers
    # --------------------------------------------------------------

    def _style_locked(self, entry: ctk.CTkEntry) -> None:
        entry.configure(
            fg_color=Palette.CELL_PREFILLED,
            text_color=Palette.CELL_TEXT_PREFILLED,
            border_color=Palette.BORDER_STRONG,
            border_width=1,
        )

    def _style_solved(self, entry: ctk.CTkEntry) -> None:
        entry.configure(
            fg_color=Palette.CELL_SOLVED,
            text_color=Palette.CELL_TEXT_SOLVED,
            border_color=Palette.SUCCESS,
            border_width=1,
        )

    def _style_reset(self, entry: ctk.CTkEntry) -> None:
        entry.configure(
            fg_color=Palette.BG_INPUT,
            text_color=Palette.CELL_TEXT,
            border_color=Palette.BORDER,
            border_width=1,
        )

    # --------------------------------------------------------------
    # Public API — read
    # --------------------------------------------------------------

    def get_matrix(self) -> List[List[str]]:
        """Matrix of strings ('' or '1'..'N')."""
        m: List[List[str]] = []
        for r in range(self.size):
            row = []
            for c in range(self.size):
                v = self.entries[r][c].get().strip()
                v = "".join(ch for ch in v if ch.isdigit())
                row.append(v)
            m.append(row)
        return m

    def get_constraints(self) -> Dict[str, str]:
        return self.constraint_state.copy()

    def get_size(self) -> int:
        return self.size

    # --------------------------------------------------------------
    # Public API — write
    # --------------------------------------------------------------

    def set_matrix(
        self,
        matrix: List[List[int]],
        mark_locked: bool = False,
        animate: bool = False,
    ) -> None:
        """Write values into the grid.

        Args:
            matrix: 2D list of ints (0 means empty).
            mark_locked: if True, mark non-zero cells as locked (prefilled).
            animate: if True, reveal newly written cells one-by-one.
        """
        if len(matrix) != self.size or any(len(row) != self.size for row in matrix):
            raise ValueError(
                f"Matrix shape {len(matrix)}x{len(matrix[0]) if matrix else 0} "
                f"does not match board size {self.size}"
            )

        # Collect deltas
        deltas: List[Tuple[int, int, int]] = []
        for r in range(self.size):
            for c in range(self.size):
                val = matrix[r][c]
                current = self.entries[r][c].get().strip()
                new_text = str(val) if val != 0 else ""
                if new_text != current:
                    deltas.append((r, c, val))

        if mark_locked:
            self._locked_cells = {(r, c) for r in range(self.size) for c in range(self.size)
                                  if matrix[r][c] != 0}

        if animate:
            self._animated_fill(deltas, mark_locked)
        else:
            for r, c, val in deltas:
                self._write_cell(r, c, val, locked=mark_locked and val != 0, solved=False)

    def _write_cell(self, r: int, c: int, val: int, locked: bool, solved: bool) -> None:
        entry = self.entries[r][c]
        entry.configure(state="normal")
        entry.delete(0, tk.END)
        if val != 0:
            entry.insert(0, str(val))

        if locked:
            self._style_locked(entry)
        elif solved:
            self._style_solved(entry)
            self._solved_cells.add((r, c))
        else:
            self._style_reset(entry)

    def _animated_fill(self, deltas: List[Tuple[int, int, int]], mark_locked: bool) -> None:
        """Reveal deltas sequentially with an easing cadence."""
        if not deltas:
            return

        # 10ms per cell for 4x4, slower for larger boards
        step_ms = max(12, 120 - (self.size * 10))

        def step(i: int = 0):
            if i >= len(deltas):
                return
            r, c, val = deltas[i]
            self._write_cell(r, c, val, locked=mark_locked and val != 0, solved=not mark_locked)
            self.after(step_ms, lambda: step(i + 1))

        step(0)

    def set_constraints(self, constraints: Dict[str, str]) -> None:
        """Display constraints.

        Accepts two formats:
        - GUI dict:    {"(r1,c1)-(r2,c2)": "<" | ">"}
        - Tuple list:  [(r1,c1,op,r2,c2), ...]  (normalised by the controller)
        """
        # Wipe UI
        for lbl in self.h_constraints.values():
            lbl.configure(text="·", text_color=Palette.TEXT_MUTED, fg_color="transparent")
        for lbl in self.v_constraints.values():
            lbl.configure(text="·", text_color=Palette.TEXT_MUTED, fg_color="transparent")

        self.constraint_state = {}
        for key, sign in constraints.items():
            self._apply_constraint_key(key, sign)

    def _apply_constraint_key(self, key: str, sign: str) -> None:
        try:
            parts = key.split("-")
            if len(parts) != 2:
                return
            r1, c1 = map(int, parts[0].strip("()").split(","))
            r2, c2 = map(int, parts[1].strip("()").split(","))
        except (ValueError, IndexError):
            return

        if r1 == r2:  # horizontal
            if c1 > c2:
                r1, c1, r2, c2 = r2, c2, r1, c1
                sign = ">" if sign == "<" else "<"
            lbl = self.h_constraints.get((r1, c1))
            if lbl:
                self.constraint_state[f"({r1},{c1})-({r2},{c2})"] = sign
                self._render_constraint(lbl, sign, horizontal=True)
        elif c1 == c2:  # vertical
            if r1 > r2:
                r1, c1, r2, c2 = r2, c2, r1, c1
                sign = ">" if sign == "<" else "<"
            lbl = self.v_constraints.get((r1, c1))
            if lbl:
                self.constraint_state[f"({r1},{c1})-({r2},{c2})"] = sign
                self._render_constraint(lbl, sign, horizontal=False)

    # --------------------------------------------------------------
    # Utility
    # --------------------------------------------------------------

    def clear_grid(self, clear_constraints: bool = False) -> None:
        for r in range(self.size):
            for c in range(self.size):
                entry = self.entries[r][c]
                entry.configure(state="normal")
                entry.delete(0, tk.END)
                self._style_reset(entry)

        self._locked_cells.clear()
        self._solved_cells.clear()
        self._error_cells = set()

        if clear_constraints:
            self.set_constraints({})

    def disable_editing(self) -> None:
        for r in range(self.size):
            for c in range(self.size):
                self.entries[r][c].configure(state="disabled")

    def enable_editing(self) -> None:
        for r in range(self.size):
            for c in range(self.size):
                self.entries[r][c].configure(state="normal")

    def resize(self, new_size: int) -> None:
        if not (4 <= new_size <= 9):
            raise ValueError("Board size must be between 4 and 9")
        if new_size == self.size:
            return
        self.size = new_size
        self.constraint_state.clear()
        self._locked_cells.clear()
        self._solved_cells.clear()
        self._error_cells = set()
        self._build_grid()
