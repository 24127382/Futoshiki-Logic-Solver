"""
Main Application Module: Futoshiki Solver GUI
==============================================

Assembles the full application:
- Top header bar with title + theme toggle
- Left sidebar with controls + stats
- Center workspace containing the Futoshiki board
- Bottom status bar
- Full keyboard shortcuts
- Wires the Controller into every user action

Run with:

    python -m gui.app

or:

    python gui/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import List, Optional

import customtkinter as ctk

# Guarantee the repo root is importable when running the file directly.
_ROOT = Path(__file__).parent.parent
for p in (_ROOT, _ROOT / "src"):
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

from gui.board_frame import BoardFrame
from gui.controller import FutoshikiController, SolverType
from gui.sidebar import Sidebar
from gui.theme import Palette, Typography, Spacing, Radii


class FutoshikiApp(ctk.CTk):
    """Main application window."""

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        super().__init__()

        # Appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=Palette.BG_BASE)

        # Window
        self.title("Futoshiki · Logic Solver")
        self.geometry("1280x820")
        self.minsize(1060, 680)

        # Internal state cache for "reset"
        self._initial_matrix: Optional[List[List[int]]] = None
        self._initial_constraints: Optional[dict] = None
        self._animate_solution = True

        # Controller
        self.controller = FutoshikiController(update_callback=self._on_controller_update)

        # Build layout
        self._build_layout()
        self._bind_shortcuts()
        self._refresh_stats_defaults()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        # ----- Top header bar -----
        self.header = ctk.CTkFrame(
            self,
            fg_color=Palette.BG_SURFACE,
            corner_radius=0,
            height=56,
            border_width=0,
        )
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)
        self._build_header()

        # ----- Bottom status bar -----
        self.footer = ctk.CTkFrame(
            self,
            fg_color=Palette.BG_SURFACE,
            corner_radius=0,
            height=28,
            border_width=0,
        )
        self.footer.pack(side="bottom", fill="x")
        self.footer.pack_propagate(False)
        self._build_footer()

        # ----- Main body: sidebar + board -----
        body = ctk.CTkFrame(self, fg_color=Palette.BG_BASE, corner_radius=0)
        body.pack(fill="both", expand=True)

        self.sidebar = Sidebar(
            body,
            on_solve=self._on_solve,
            on_stop=self._on_stop,
            on_clear=self._on_clear,
            on_reset=self._on_reset,
            on_load=self._on_load,
            on_save=self._on_save,
            on_size_change=self._on_size_change,
            on_algorithm_change=self._on_algorithm_change,
            on_animate_toggle=self._on_animate_toggle,
        )
        self.sidebar.pack(side="left", fill="y")

        # Divider between sidebar and workspace
        divider = ctk.CTkFrame(body, fg_color=Palette.BORDER, width=1, corner_radius=0)
        divider.pack(side="left", fill="y")

        # Workspace wraps the board so we can center it
        workspace = ctk.CTkFrame(body, fg_color=Palette.BG_BASE, corner_radius=0)
        workspace.pack(side="left", fill="both", expand=True)
        self._workspace = workspace

        self.board_frame = BoardFrame(
            workspace,
            size=self.sidebar.get_size(),
            editable_constraints=True,
        )
        # Center the board in the workspace
        self.board_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Re-center on resize
        workspace.bind("<Configure>", lambda e: self.board_frame.place(relx=0.5, rely=0.5, anchor="center"))

    def _build_header(self) -> None:
        inner = ctk.CTkFrame(self.header, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=Spacing.XL)

        # Left: wordmark
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y")

        ctk.CTkLabel(
            left,
            text="◆ Futoshiki",
            font=(Typography.FAMILY, 18, "bold"),
            text_color=Palette.ACCENT,
        ).pack(side="left", pady=Spacing.MD)

        ctk.CTkLabel(
            left,
            text="  ·  Logic Solver",
            font=Typography.body(),
            text_color=Palette.TEXT_SECONDARY,
        ).pack(side="left", pady=Spacing.MD)

        # Right: theme toggle + help
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right", fill="y")

        self._theme_btn = ctk.CTkButton(
            right,
            text="☾  Dark",
            width=86,
            height=30,
            corner_radius=Radii.MD,
            font=Typography.body_bold(),
            fg_color=Palette.BG_ELEVATED,
            hover_color=Palette.BG_HOVER,
            text_color=Palette.TEXT_PRIMARY,
            border_color=Palette.BORDER,
            border_width=1,
            command=self._toggle_theme,
        )
        self._theme_btn.pack(side="right", padx=(0, 0), pady=Spacing.MD)

        ctk.CTkButton(
            right,
            text="?",
            width=30,
            height=30,
            corner_radius=Radii.MD,
            font=Typography.body_bold(),
            fg_color=Palette.BG_ELEVATED,
            hover_color=Palette.BG_HOVER,
            text_color=Palette.TEXT_PRIMARY,
            border_color=Palette.BORDER,
            border_width=1,
            command=self._show_help,
        ).pack(side="right", padx=(0, 8), pady=Spacing.MD)

    def _build_footer(self) -> None:
        inner = ctk.CTkFrame(self.footer, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=Spacing.XL)

        self._footer_status = ctk.CTkLabel(
            inner,
            text="Ready.",
            font=Typography.small(),
            text_color=Palette.TEXT_SECONDARY,
        )
        self._footer_status.pack(side="left")

        self._footer_hint = ctk.CTkLabel(
            inner,
            text="Ctrl+Enter solve   ·   Ctrl+L clear   ·   Ctrl+O open   ·   Ctrl+S save",
            font=Typography.small(),
            text_color=Palette.TEXT_MUTED,
        )
        self._footer_hint.pack(side="right")

    # ------------------------------------------------------------------
    # Keyboard shortcuts
    # ------------------------------------------------------------------

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-Return>", lambda e: self._on_solve())
        self.bind("<Control-l>", lambda e: self._on_clear())
        self.bind("<Control-L>", lambda e: self._on_clear())
        self.bind("<Control-o>", lambda e: self._on_load())
        self.bind("<Control-O>", lambda e: self._on_load())
        self.bind("<Control-s>", lambda e: self._on_save())
        self.bind("<Control-S>", lambda e: self._on_save())
        self.bind("<Escape>", lambda e: self._on_stop())

    # ------------------------------------------------------------------
    # Handlers from the sidebar
    # ------------------------------------------------------------------

    def _on_solve(self) -> None:
        gui_matrix = self.board_frame.get_matrix()
        gui_constraints = self.board_frame.get_constraints()
        size = self.board_frame.get_size()

        # Snapshot initial state so "Reset" can restore it later
        try:
            self._initial_matrix = self.controller._gui_to_int_matrix(gui_matrix, size)
        except Exception:
            self._initial_matrix = None
        self._initial_constraints = dict(gui_constraints)

        self.controller.set_timeout(self.sidebar.get_timeout())
        self.sidebar.set_solving(True)
        self.board_frame.highlight_errors([])
        self._set_footer("Solving with " + self.sidebar.get_algorithm() + "…", Palette.WARNING)

        self.controller.handle_solve_request(
            gui_matrix,
            gui_constraints,
            size,
            self.sidebar.get_algorithm(),
        )

    def _on_stop(self) -> None:
        if self.controller.is_solving:
            self.controller.cancel_solve()
            self._set_footer("Cancelling…", Palette.WARNING)

    def _on_clear(self) -> None:
        self.board_frame.clear_grid(clear_constraints=False)
        self.board_frame.enable_editing()
        self.sidebar.update_stats(elapsed=0.0, nodes=0, outcome="—", outcome_level="idle")
        self.sidebar.update_status("Grid cleared", "idle")
        self._set_footer("Grid cleared.", Palette.TEXT_SECONDARY)

    def _on_reset(self) -> None:
        if self._initial_matrix is None:
            self._on_clear()
            return
        size = self.board_frame.get_size()
        self.board_frame.clear_grid(clear_constraints=False)
        self.board_frame.set_matrix(self._initial_matrix, mark_locked=True, animate=False)
        if self._initial_constraints is not None:
            self.board_frame.set_constraints(self._initial_constraints)
        self.board_frame.enable_editing()
        self._set_footer("Reset to initial puzzle.", Palette.INFO)
        self.sidebar.update_status("Ready", "idle")

    def _on_load(self) -> None:
        path = filedialog.askopenfilename(
            title="Open Futoshiki puzzle",
            initialdir=str(_ROOT / "inputs"),
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            matrix, constraints_gui, size = self.controller.load_puzzle_from_file(path)
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Load failed", f"Cannot load puzzle:\n{e}")
            return

        # Resize and populate
        if size != self.board_frame.get_size():
            self.board_frame.resize(size)
            self.sidebar.set_size(size)
        self.board_frame.clear_grid(clear_constraints=True)
        self.board_frame.set_matrix(matrix, mark_locked=True, animate=False)
        self.board_frame.set_constraints(constraints_gui)
        self.board_frame.enable_editing()

        self._initial_matrix = [list(row) for row in matrix]
        self._initial_constraints = dict(constraints_gui)

        file_name = Path(path).name
        self._set_footer(f"Loaded {file_name} ({size}×{size})", Palette.SUCCESS)
        self.sidebar.update_status(f"Loaded {file_name}", "ok")

    def _on_save(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save puzzle as…",
            initialdir=str(_ROOT / "inputs"),
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return

        size = self.board_frame.get_size()
        try:
            matrix = self.controller._gui_to_int_matrix(self.board_frame.get_matrix(), size)
        except ValueError as e:
            messagebox.showerror("Save failed", f"Grid is invalid: {e}")
            return

        try:
            self.controller.save_puzzle_to_file(
                path, matrix, self.board_frame.get_constraints(), size
            )
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Save failed", f"Cannot save puzzle:\n{e}")
            return

        self._set_footer(f"Saved to {Path(path).name}", Palette.SUCCESS)
        self.sidebar.update_status(f"Saved {Path(path).name}", "ok")

    def _on_size_change(self, size: int) -> None:
        if self.board_frame.get_size() == size:
            return
        self.board_frame.resize(size)
        self._initial_matrix = None
        self._initial_constraints = None
        self._set_footer(f"Grid resized to {size}×{size}", Palette.INFO)

    def _on_algorithm_change(self, algorithm: str) -> None:
        self.sidebar.update_stats(algorithm=algorithm)
        self._set_footer(f"Algorithm set: {algorithm}", Palette.INFO)

    def _on_animate_toggle(self, animate: bool) -> None:
        self._animate_solution = animate
        self._set_footer(
            f"Solution animation {'on' if animate else 'off'}",
            Palette.TEXT_SECONDARY,
        )

    # ------------------------------------------------------------------
    # Controller updates -> UI (must marshal to main thread)
    # ------------------------------------------------------------------

    def _on_controller_update(self, status: str, data: dict) -> None:
        self.after(0, self._apply_controller_update, status, data or {})

    def _apply_controller_update(self, status: str, data: dict) -> None:
        if status == "solving":
            self.sidebar.set_solving(True)
            self.sidebar.update_status("Solving…", "busy")
            self.sidebar.update_stats(
                algorithm=data.get("algorithm", self.sidebar.get_algorithm()),
                outcome="Running", outcome_level="busy",
            )
            return

        # Any other status stops the solving UI
        self.sidebar.set_solving(False)
        elapsed = data.get("elapsed", 0.0)
        nodes = data.get("nodes", 0)
        self.sidebar.update_stats(elapsed=elapsed, nodes=nodes)

        if status == "success":
            solution = data.get("solution")
            if solution:
                self.board_frame.set_matrix(
                    solution, mark_locked=False, animate=self._animate_solution
                )
            self.sidebar.update_status("Solved", "ok")
            self.sidebar.update_stats(outcome="Solved", outcome_level="ok")
            self._set_footer(
                f"Solved in {self._fmt_time(elapsed)} · {nodes:,} steps",
                Palette.SUCCESS,
            )
            self._toast("Puzzle solved successfully!", "ok")
        elif status == "unsolvable":
            self.sidebar.update_status("Unsolvable", "error")
            self.sidebar.update_stats(outcome="Unsolvable", outcome_level="error")
            self._set_footer("No solution satisfies the constraints.", Palette.ERROR)
            self._toast("This puzzle has no solution.", "error")
        elif status == "timeout":
            self.sidebar.update_status("Timed out", "error")
            self.sidebar.update_stats(outcome="Timeout", outcome_level="error")
            self._set_footer(data.get("message", "Timed out"), Palette.ERROR)
            self._toast(data.get("message", "Timed out"), "error")
        elif status == "cancelled":
            self.sidebar.update_status("Cancelled", "idle")
            self.sidebar.update_stats(outcome="Cancelled", outcome_level="idle")
            self._set_footer("Solver cancelled.", Palette.TEXT_SECONDARY)
        elif status == "error":
            msg = data.get("message", "Unknown error")
            self.sidebar.update_status("Error", "error")
            self.sidebar.update_stats(outcome="Error", outcome_level="error")
            self._set_footer(msg, Palette.ERROR)
            self._toast(msg, "error")
            conflicts = data.get("conflict_cells")
            if conflicts:
                self.board_frame.highlight_errors(list(conflicts))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _refresh_stats_defaults(self) -> None:
        self.sidebar.update_stats(
            algorithm=self.sidebar.get_algorithm(),
            elapsed=0.0,
            nodes=0,
            outcome="—",
            outcome_level="idle",
        )

    def _set_footer(self, text: str, color: str) -> None:
        self._footer_status.configure(text=text, text_color=color)

    def _fmt_time(self, elapsed: float) -> str:
        if elapsed < 1:
            return f"{elapsed*1000:.1f} ms"
        return f"{elapsed:.3f} s"

    def _toggle_theme(self) -> None:
        current = ctk.get_appearance_mode()
        if current.lower() == "dark":
            ctk.set_appearance_mode("light")
            self._theme_btn.configure(text="☀  Light")
        else:
            ctk.set_appearance_mode("dark")
            self._theme_btn.configure(text="☾  Dark")

    def _show_help(self) -> None:
        messagebox.showinfo(
            "Futoshiki — Help",
            "HOW TO USE\n"
            "──────────\n"
            " • Type a digit 1..N into any cell\n"
            " • Click the small gap between two cells to set < / >\n"
            " • Clicking a constraint again cycles < → > → none\n"
            " • Use arrow keys to move between cells\n\n"
            "SHORTCUTS\n"
            "─────────\n"
            "  Ctrl+Enter    Solve\n"
            "  Ctrl+L        Clear grid\n"
            "  Ctrl+O        Open file\n"
            "  Ctrl+S        Save file\n"
            "  Esc           Stop solver\n",
        )

    def _toast(self, text: str, level: str) -> None:
        """Tiny, non-blocking message. We use message boxes for important ones."""
        # For important statuses we keep the old messagebox behaviour
        if level == "error":
            messagebox.showwarning("Futoshiki", text)
        elif level == "ok":
            messagebox.showinfo("Futoshiki", text)

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self) -> None:
        self.mainloop()


def main() -> None:
    app = FutoshikiApp()
    app.run()


if __name__ == "__main__":
    main()
