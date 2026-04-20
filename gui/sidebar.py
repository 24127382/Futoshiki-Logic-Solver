"""
Sidebar Module: Controls, stats, and actions
=============================================
Left-hand control panel for the Futoshiki app. Contains:
- Brand header
- Grid size picker (4..9)
- Algorithm picker (Backtracking / Forward Chaining / Backward Chaining / A*)
- Timeout slider
- Primary actions (Solve, Stop, Clear, Reset)
- File I/O (Load / Save)
- Live status + stats card
- Tips / help hint
"""

from __future__ import annotations

from enum import Enum
from typing import Callable, Optional

import customtkinter as ctk

from gui.theme import Palette, Typography, Spacing, Radii


class SolverType(str, Enum):
    BACKTRACKING = "Backtracking"
    FORWARD_CHAINING = "Forward Chaining"
    BACKWARD_CHAINING = "Backward Chaining"
    A_STAR = "A*"


class Sidebar(ctk.CTkFrame):
    """Left sidebar with controls + stats."""

    def __init__(
        self,
        parent,
        on_solve: Callable[[], None],
        on_stop: Optional[Callable[[], None]] = None,
        on_clear: Optional[Callable[[], None]] = None,
        on_reset: Optional[Callable[[], None]] = None,
        on_load: Optional[Callable[[], None]] = None,
        on_save: Optional[Callable[[], None]] = None,
        on_size_change: Optional[Callable[[int], None]] = None,
        on_algorithm_change: Optional[Callable[[str], None]] = None,
        on_animate_toggle: Optional[Callable[[bool], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            width=320,
            fg_color=Palette.BG_SURFACE,
            corner_radius=0,
            **kwargs,
        )
        self.pack_propagate(False)

        self.on_solve = on_solve
        self.on_stop = on_stop
        self.on_clear = on_clear
        self.on_reset = on_reset
        self.on_load = on_load
        self.on_save = on_save
        self.on_size_change = on_size_change
        self.on_algorithm_change = on_algorithm_change
        self.on_animate_toggle = on_animate_toggle

        self.size_var = ctk.IntVar(value=5)
        self.algorithm_var = ctk.StringVar(value=SolverType.FORWARD_CHAINING.value)
        self.timeout_var = ctk.IntVar(value=30)
        self.animate_var = ctk.BooleanVar(value=True)

        self._stat_rows = {}
        self._build()

    def _build(self) -> None:
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Palette.BG_ELEVATED,
            scrollbar_button_hover_color=Palette.BG_HOVER,
        )
        self._scroll.pack(fill="both", expand=True)

        self._build_header()
        self._build_size_section()
        self._build_algorithm_section()
        self._build_timeout_section()
        self._build_options_section()
        self._build_action_buttons()
        self._build_file_buttons()
        self._build_stats_card()
        self._build_tips()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self._scroll, fg_color="transparent")
        header.pack(fill="x", padx=Spacing.XL, pady=(Spacing.XL, Spacing.MD))

        ctk.CTkLabel(
            header,
            text="\u25C6",
            font=(Typography.FAMILY, 34, "bold"),
            text_color=Palette.ACCENT,
        ).pack(side="left", padx=(0, Spacing.MD))

        text_frame = ctk.CTkFrame(header, fg_color="transparent")
        text_frame.pack(side="left", fill="y")

        ctk.CTkLabel(
            text_frame,
            text="Futoshiki",
            font=(Typography.FAMILY, 22, "bold"),
            text_color=Palette.TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_frame,
            text="Logic Solver",
            font=Typography.small(),
            text_color=Palette.TEXT_SECONDARY,
        ).pack(anchor="w")

        self._divider(self._scroll)

    def _build_size_section(self) -> None:
        self._section_title("Grid Size")

        ctk.CTkLabel(
            self._scroll,
            text="Choose a board dimension from 4x4 up to 9x9.",
            font=Typography.small(),
            text_color=Palette.TEXT_MUTED,
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.SM))

        seg = ctk.CTkSegmentedButton(
            self._scroll,
            values=["4", "5", "6", "7", "8", "9"],
            command=self._handle_size_change,
            fg_color=Palette.BG_ELEVATED,
            selected_color=Palette.ACCENT,
            selected_hover_color=Palette.ACCENT_HOVER,
            unselected_color=Palette.BG_ELEVATED,
            unselected_hover_color=Palette.BG_HOVER,
            text_color=Palette.TEXT_PRIMARY,
            font=Typography.body_bold(),
            height=34,
            corner_radius=Radii.MD,
        )
        seg.set(str(self.size_var.get()))
        seg.pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.MD))
        self._size_segmented = seg

        self._divider(self._scroll)

    def _build_algorithm_section(self) -> None:
        self._section_title("Algorithm")

        algo_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
        algo_frame.pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.MD))

        options = [
            (SolverType.FORWARD_CHAINING.value, "Unit propagation over CNF (fast)"),
            (SolverType.BACKWARD_CHAINING.value, "DPLL-style SAT search on CNF"),
            (SolverType.BACKTRACKING.value, "Classic DFS with constraint checks"),
            (SolverType.A_STAR.value, "Heuristic search (experimental)"),
        ]

        for name, desc in options:
            row = ctk.CTkFrame(algo_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            ctk.CTkRadioButton(
                row,
                text=name,
                variable=self.algorithm_var,
                value=name,
                command=self._handle_algorithm_change,
                font=Typography.body_bold(),
                text_color=Palette.TEXT_PRIMARY,
                fg_color=Palette.ACCENT,
                hover_color=Palette.ACCENT_HOVER,
                border_color=Palette.BORDER_STRONG,
            ).pack(anchor="w")

            ctk.CTkLabel(
                row,
                text=desc,
                font=Typography.small(),
                text_color=Palette.TEXT_MUTED,
            ).pack(anchor="w", padx=(28, 0))

        self._divider(self._scroll)

    def _build_timeout_section(self) -> None:
        self._section_title("Timeout")

        header = ctk.CTkFrame(self._scroll, fg_color="transparent")
        header.pack(fill="x", padx=Spacing.XL)

        ctk.CTkLabel(
            header,
            text="Stop solver after",
            font=Typography.small(),
            text_color=Palette.TEXT_SECONDARY,
        ).pack(side="left")

        self._timeout_value_label = ctk.CTkLabel(
            header,
            text=str(self.timeout_var.get()) + " s",
            font=Typography.body_bold(),
            text_color=Palette.ACCENT,
        )
        self._timeout_value_label.pack(side="right")

        slider = ctk.CTkSlider(
            self._scroll,
            from_=5,
            to=120,
            number_of_steps=23,
            command=self._handle_timeout_change,
            progress_color=Palette.ACCENT,
            button_color=Palette.ACCENT,
            button_hover_color=Palette.ACCENT_HOVER,
            fg_color=Palette.BG_ELEVATED,
        )
        slider.set(self.timeout_var.get())
        slider.pack(fill="x", padx=Spacing.XL, pady=(Spacing.SM, Spacing.MD))

        self._divider(self._scroll)

    def _build_options_section(self) -> None:
        self._section_title("Options")

        box = ctk.CTkFrame(self._scroll, fg_color="transparent")
        box.pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.MD))

        ctk.CTkSwitch(
            box,
            text="Animate solver output",
            variable=self.animate_var,
            command=self._handle_animate_toggle,
            font=Typography.body(),
            text_color=Palette.TEXT_PRIMARY,
            progress_color=Palette.ACCENT,
            button_color=Palette.TEXT_PRIMARY,
            button_hover_color=Palette.TEXT_SECONDARY,
        ).pack(anchor="w")

        self._divider(self._scroll)

    def _build_action_buttons(self) -> None:
        self._section_title("Actions")

        row1 = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row1.pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.SM))

        self.solve_btn = ctk.CTkButton(
            row1,
            text="\u25B6  Solve",
            command=self._handle_solve,
            font=Typography.subheading(),
            fg_color=Palette.ACCENT,
            hover_color=Palette.ACCENT_HOVER,
            text_color="#FFFFFF",
            height=44,
            corner_radius=Radii.MD,
        )
        self.solve_btn.pack(fill="x")

        row2 = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row2.pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.SM))

        self.stop_btn = ctk.CTkButton(
            row2,
            text="\u25A0  Stop",
            command=self._handle_stop,
            font=Typography.body_bold(),
            fg_color=Palette.BG_ELEVATED,
            hover_color=Palette.ERROR_SOFT,
            text_color=Palette.ERROR,
            border_color=Palette.BORDER,
            border_width=1,
            height=34,
            corner_radius=Radii.MD,
            state="disabled",
        )
        self.stop_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self.clear_btn = ctk.CTkButton(
            row2,
            text="\u232B  Clear",
            command=self._handle_clear,
            font=Typography.body_bold(),
            fg_color=Palette.BG_ELEVATED,
            hover_color=Palette.BG_HOVER,
            text_color=Palette.TEXT_PRIMARY,
            border_color=Palette.BORDER,
            border_width=1,
            height=34,
            corner_radius=Radii.MD,
        )
        self.clear_btn.pack(side="left", expand=True, fill="x", padx=(4, 0))

        self.reset_btn = ctk.CTkButton(
            self._scroll,
            text="\u21BA  Reset to initial puzzle",
            command=self._handle_reset,
            font=Typography.small(),
            fg_color="transparent",
            hover_color=Palette.BG_HOVER,
            text_color=Palette.TEXT_SECONDARY,
            height=28,
            corner_radius=Radii.SM,
        )
        self.reset_btn.pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.MD))

        self._divider(self._scroll)

    def _build_file_buttons(self) -> None:
        self._section_title("Puzzle File")

        row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row.pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.MD))

        ctk.CTkButton(
            row,
            text="Load",
            command=self._handle_load,
            font=Typography.body_bold(),
            fg_color=Palette.BG_ELEVATED,
            hover_color=Palette.BG_HOVER,
            text_color=Palette.TEXT_PRIMARY,
            border_color=Palette.BORDER,
            border_width=1,
            height=34,
            corner_radius=Radii.MD,
        ).pack(side="left", expand=True, fill="x", padx=(0, 4))

        ctk.CTkButton(
            row,
            text="Save",
            command=self._handle_save,
            font=Typography.body_bold(),
            fg_color=Palette.BG_ELEVATED,
            hover_color=Palette.BG_HOVER,
            text_color=Palette.TEXT_PRIMARY,
            border_color=Palette.BORDER,
            border_width=1,
            height=34,
            corner_radius=Radii.MD,
        ).pack(side="left", expand=True, fill="x", padx=(4, 0))

        self._divider(self._scroll)

    def _build_stats_card(self) -> None:
        self._section_title("Status & Stats")

        card = ctk.CTkFrame(
            self._scroll,
            fg_color=Palette.BG_ELEVATED,
            corner_radius=Radii.LG,
            border_width=1,
            border_color=Palette.BORDER,
        )
        card.pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.MD))

        status_row = ctk.CTkFrame(card, fg_color="transparent")
        status_row.pack(fill="x", padx=Spacing.LG, pady=(Spacing.MD, Spacing.SM))

        self._status_dot = ctk.CTkLabel(
            status_row,
            text="\u25CF",
            font=(Typography.FAMILY, 14, "bold"),
            text_color=Palette.TEXT_MUTED,
        )
        self._status_dot.pack(side="left", padx=(0, 6))

        self._status_label = ctk.CTkLabel(
            status_row,
            text="Ready",
            font=Typography.body_bold(),
            text_color=Palette.TEXT_PRIMARY,
        )
        self._status_label.pack(side="left")

        self._progress = ctk.CTkProgressBar(
            card,
            mode="indeterminate",
            height=4,
            corner_radius=2,
            progress_color=Palette.ACCENT,
            fg_color=Palette.BG_INPUT,
        )
        self._progress.set(0)
        self._progress.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))

        self._stat_rows = {}
        stats = [
            ("algo", "Algorithm", self.algorithm_var.get()),
            ("time", "Elapsed time", "-"),
            ("nodes", "Nodes / steps", "-"),
            ("status_detail", "Outcome", "-"),
        ]
        for key, label, value in stats:
            self._stat_rows[key] = self._add_stat_row(card, label, value)

        ctk.CTkFrame(card, fg_color="transparent", height=Spacing.MD).pack()

    def _add_stat_row(self, parent, label: str, value: str):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=Spacing.LG, pady=2)

        ctk.CTkLabel(
            row,
            text=label,
            font=Typography.small(),
            text_color=Palette.TEXT_SECONDARY,
        ).pack(side="left")

        val_lbl = ctk.CTkLabel(
            row,
            text=value,
            font=Typography.mono(),
            text_color=Palette.TEXT_PRIMARY,
        )
        val_lbl.pack(side="right")
        return val_lbl

    def _build_tips(self) -> None:
        self._divider(self._scroll)
        self._section_title("Tips")

        tips = (
            "- Type digits 1-N into cells\n"
            "- Click the gap between two cells to set < or >\n"
            "- Arrow keys navigate the board\n"
            "- Ctrl+Enter solves,  Ctrl+L clears\n"
        )
        ctk.CTkLabel(
            self._scroll,
            text=tips,
            font=Typography.small(),
            text_color=Palette.TEXT_MUTED,
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.XXL))

    def _section_title(self, text: str) -> None:
        ctk.CTkLabel(
            self._scroll,
            text=text.upper(),
            font=(Typography.FAMILY, Typography.SIZE_SM, "bold"),
            text_color=Palette.TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=Spacing.XL, pady=(Spacing.MD, Spacing.SM))

    def _divider(self, parent) -> None:
        line = ctk.CTkFrame(parent, fg_color=Palette.BORDER, height=1)
        line.pack(fill="x", padx=Spacing.XL, pady=Spacing.XS)

    def _handle_size_change(self, value: str) -> None:
        new_size = int(value)
        self.size_var.set(new_size)
        if self.on_size_change:
            self.on_size_change(new_size)

    def _handle_algorithm_change(self) -> None:
        if self.on_algorithm_change:
            self.on_algorithm_change(self.algorithm_var.get())
        self.update_stats(algorithm=self.algorithm_var.get())

    def _handle_timeout_change(self, value: float) -> None:
        val = int(round(value))
        self.timeout_var.set(val)
        self._timeout_value_label.configure(text=str(val) + " s")

    def _handle_animate_toggle(self) -> None:
        if self.on_animate_toggle:
            self.on_animate_toggle(bool(self.animate_var.get()))

    def _handle_solve(self) -> None:
        self.on_solve()

    def _handle_stop(self) -> None:
        if self.on_stop:
            self.on_stop()

    def _handle_clear(self) -> None:
        if self.on_clear:
            self.on_clear()

    def _handle_reset(self) -> None:
        if self.on_reset:
            self.on_reset()

    def _handle_load(self) -> None:
        if self.on_load:
            self.on_load()

    def _handle_save(self) -> None:
        if self.on_save:
            self.on_save()

    def get_size(self) -> int:
        return int(self.size_var.get())

    def get_algorithm(self) -> str:
        return self.algorithm_var.get()

    def get_timeout(self) -> int:
        return int(self.timeout_var.get())

    def get_animate(self) -> bool:
        return bool(self.animate_var.get())

    def set_size(self, size: int) -> None:
        self.size_var.set(size)
        self._size_segmented.set(str(size))

    def set_solving(self, solving: bool) -> None:
        if solving:
            self.solve_btn.configure(state="disabled", text="Solving...")
            self.stop_btn.configure(state="normal")
            self._progress.start()
            self.update_status("Solving", "busy")
        else:
            self.solve_btn.configure(state="normal", text="\u25B6  Solve")
            self.stop_btn.configure(state="disabled")
            self._progress.stop()
            self._progress.set(0)

    def update_status(self, text: str, level: str = "idle") -> None:
        color_map = {
            "idle": Palette.TEXT_MUTED,
            "busy": Palette.WARNING,
            "ok": Palette.SUCCESS,
            "error": Palette.ERROR,
            "info": Palette.INFO,
        }
        self._status_dot.configure(text_color=color_map.get(level, Palette.TEXT_MUTED))
        self._status_label.configure(text=text)

    def update_stats(
        self,
        algorithm=None,
        elapsed=None,
        nodes=None,
        outcome=None,
        outcome_level="idle",
    ) -> None:
        if algorithm is not None:
            self._stat_rows["algo"].configure(text=algorithm)
        if elapsed is not None:
            text = f"{elapsed*1000:.1f} ms" if elapsed < 1 else f"{elapsed:.3f} s"
            self._stat_rows["time"].configure(text=text)
        if nodes is not None:
            self._stat_rows["nodes"].configure(text=f"{nodes:,}")
        if outcome is not None:
            color_map = {
                "idle": Palette.TEXT_PRIMARY,
                "ok": Palette.SUCCESS,
                "error": Palette.ERROR,
                "info": Palette.INFO,
                "busy": Palette.WARNING,
            }
            self._stat_rows["status_detail"].configure(
                text=outcome, text_color=color_map.get(outcome_level, Palette.TEXT_PRIMARY)
            )
