"""
Sidebar Module: Control Panel
=============================
The sidebar contains:
- File loader (Open puzzle from .txt)
- Grid size selector (4x4 to 9x9)
- Algorithm selector (Backtracking, Forward Chaining, A*)
- Solve button
- Clear button
- Status display
- Solver stats display

Responsibility:
- Collect user inputs
- Trigger controller actions
- Display status/results
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable, Optional, Dict, Any
import customtkinter as ctk
from gui.controller import SolverType
import os


class Sidebar(ctk.CTkFrame):
    """
    Control panel sidebar on the left.

    Contains all user controls and status displays.
    """

    def __init__(self, parent, on_solve_click: Callable = None, **kwargs):
        """
        Initialize the sidebar.

        Args:
            parent: Parent tkinter widget
            on_solve_click: Callback when "Solve" button clicked
                          Signature: on_solve_click(size, algorithm)
            **kwargs: Passed to CTkFrame
        """
        super().__init__(parent, **kwargs)

        # Callbacks
        self.on_solve_click = on_solve_click or self._default_callback
        self.on_file_load = None
        self.on_size_change = None

        # State
        self.current_size = 4
        self.current_algorithm = SolverType.BACKTRACKING
        self.is_solving = False
        self.constraint_mode = False

        # Callbacks for constraint mode
        self.on_constraint_mode_toggle = None
        self.on_clear_click = None

        # Create widgets
        self._create_widgets()

    def _default_callback(self, *args, **kwargs):
        """Default no-op callback."""
        pass

    # ========================================================================
    # WIDGET CREATION
    # ========================================================================

    def _create_widgets(self) -> None:
        """Create all sidebar widgets with scrollable frame."""
        # Title (pinned at top)
        title = ctk.CTkLabel(
            self,
            text="Futoshiki Solver",
            font=("Arial", 18, "bold")
        )
        title.pack(padx=10, pady=10)

        # ====================================================================
        # SCROLLABLE CONTAINER (all controls go here)
        # ====================================================================
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # ====================================================================
        # FILE SECTION
        # ====================================================================
        file_frame = ctk.CTkFrame(self.scrollable_frame)
        file_frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(file_frame, text="📁 Load Puzzle", font=("Arial", 12, "bold")).pack()

        self.file_button = ctk.CTkButton(
            file_frame,
            text="Open File",
            command=self._on_file_open,
            fg_color="#0066cc",
            hover_color="#0052a3"
        )
        self.file_button.pack(pady=5, fill="x")

        self.file_label = ctk.CTkLabel(file_frame, text="No file loaded", text_color="gray")
        self.file_label.pack(pady=2)

        # ====================================================================
        # GRID SIZE SECTION
        # ====================================================================
        size_frame = ctk.CTkFrame(self.scrollable_frame)
        size_frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(size_frame, text="🔲 Grid Size", font=("Arial", 12, "bold")).pack()

        self.size_var = tk.IntVar(value=4)

        # Radio buttons for sizes 4-9
        for size in range(4, 10):
            rb = ctk.CTkRadioButton(
                size_frame,
                text=f"{size}×{size}",
                variable=self.size_var,
                value=size,
                command=self._on_size_change
            )
            rb.pack(anchor="w", padx=10, pady=2)

        # ====================================================================
        # ALGORITHM SECTION
        # ====================================================================
        algo_frame = ctk.CTkFrame(self.scrollable_frame)
        algo_frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(algo_frame, text="⚙️ Algorithm", font=("Arial", 12, "bold")).pack()

        self.algo_var = tk.StringVar(value=SolverType.BACKTRACKING.value)

        algorithms = [
            (SolverType.BACKTRACKING, "Backtracking"),
            (SolverType.FORWARD_CHAINING, "Forward Chaining"),
            (SolverType.BACKWARD_CHAINING, "Backward Chaining"),
            (SolverType.A_STAR, "A*"),
        ]

        for algo_type, label in algorithms:
            rb = ctk.CTkRadioButton(
                algo_frame,
                text=label,
                variable=self.algo_var,
                value=algo_type.value,
                command=self._on_algo_change
            )
            rb.pack(anchor="w", padx=10, pady=2)

        # ====================================================================
        # TIMEOUT SECTION
        # ====================================================================
        timeout_frame = ctk.CTkFrame(self.scrollable_frame)
        timeout_frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(timeout_frame, text="⏱️ Timeout (seconds)", font=("Arial", 12, "bold")).pack()

        self.timeout_var = tk.StringVar(value="30")

        self.timeout_entry = ctk.CTkEntry(
            timeout_frame,
            textvariable=self.timeout_var,
            width=100
        )
        self.timeout_entry.pack(pady=5)

        # ====================================================================
        # CONSTRAINT MODE TOGGLE
        # ====================================================================
        constraint_frame = ctk.CTkFrame(self.scrollable_frame)
        constraint_frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(constraint_frame, text="✏️ Input Mode", font=("Arial", 12, "bold")).pack()

        self.constraint_mode_var = tk.BooleanVar(value=False)

        mode_option_frame = ctk.CTkFrame(constraint_frame)
        mode_option_frame.pack(fill="x", pady=5)

        ctk.CTkRadioButton(
            mode_option_frame,
            text="Value Input",
            variable=self.constraint_mode_var,
            value=False,
            command=self._on_constraint_mode_change
        ).pack(anchor="w", padx=10, pady=2)

        ctk.CTkRadioButton(
            mode_option_frame,
            text="Create Constraints",
            variable=self.constraint_mode_var,
            value=True,
            command=self._on_constraint_mode_change
        ).pack(anchor="w", padx=10, pady=2)

        # ====================================================================
        # STATUS DISPLAY
        # ====================================================================
        status_frame = ctk.CTkFrame(self.scrollable_frame)
        status_frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(status_frame, text="📊 Status", font=("Arial", 12, "bold")).pack()

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            text_color="#00cc66",
            font=("Arial", 11)
        )
        self.status_label.pack(pady=5)

        # ====================================================================
        # STATS DISPLAY
        # ====================================================================
        stats_frame = ctk.CTkFrame(self.scrollable_frame)
        stats_frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(stats_frame, text="📈 Solver Stats", font=("Arial", 12, "bold")).pack()

        self.stats_text = ctk.CTkTextbox(
            stats_frame,
            height=100,
            width=250,
            font=("Courier", 9),
            state="disabled"
        )
        self.stats_text.pack(pady=5, fill="both", expand=True)

        # ====================================================================
        # ACTION BUTTONS (at bottom, pinned)
        # ====================================================================
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(padx=10, pady=15, fill="x", side="bottom")

        self.solve_button = ctk.CTkButton(
            button_frame,
            text="▶ SOLVE",
            command=self._on_solve_click,
            fg_color="#00cc66",
            hover_color="#00aa55",
            font=("Arial", 14, "bold"),
            height=40
        )
        self.solve_button.pack(pady=5, fill="x")

        self.clear_button = ctk.CTkButton(
            button_frame,
            text="🗑️ Clear Grid",
            command=self._on_clear_click,
            fg_color="#cc6600",
            hover_color="#aa5500",
            height=35
        )
        self.clear_button.pack(pady=5, fill="x")

    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================

    def _on_file_open(self) -> None:
        """Handle file open dialog."""
        filetypes = [("Text files", "*.txt"), ("All files", "*.*")]

        # Calculate the absolute path to the inputs/ directory
        # (sidebar.py is inside gui/, so we go up one level then into inputs/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        inputs_dir = os.path.join(os.path.dirname(current_dir), "inputs")

        filepath = filedialog.askopenfilename(
            title="Open Futoshiki Puzzle",
            filetypes=filetypes,
            initialdir=inputs_dir  # Tell the dialog to start here
        )

        if filepath:
            self.file_label.configure(text=filepath.split("/")[-1])
            if self.on_file_load:
                self.on_file_load(filepath)

    def _on_size_change(self) -> None:
        """Handle size radio button change."""
        new_size = self.size_var.get()
        self.current_size = new_size
        if self.on_size_change:
            self.on_size_change(new_size)

    def _on_algo_change(self) -> None:
        """Handle algorithm radio button change."""
        algo_value = self.algo_var.get()
        self.current_algorithm = SolverType(algo_value)

    def _on_constraint_mode_change(self) -> None:
        """Handle constraint mode toggle."""
        self.constraint_mode = self.constraint_mode_var.get()
        if self.on_constraint_mode_toggle:
            self.on_constraint_mode_toggle(self.constraint_mode)

    def _on_solve_click(self) -> None:
        """Handle Solve button click."""
        if self.is_solving:
            messagebox.showwarning("Solving", "Already solving. Please wait.")
            return

        # 2. Safe conversion: if empty or invalid, default to 30
        try:
            raw_val = self.timeout_var.get()
            timeout = int(raw_val) if raw_val.strip() else 30
        except ValueError:
            timeout = 30

        # Call callback with current state
        self.on_solve_click(
            size=self.current_size,
            algorithm=self.current_algorithm,
            timeout=timeout
        )

    def _on_clear_click(self) -> None:
        """Handle Clear button click."""
        if messagebox.askyesno("Confirm", "Clear all values and constraints?"):
            # Call the parent app's clear function if it exists
            if hasattr(self, 'on_clear_click') and self.on_clear_click:
                self.on_clear_click()

    # ========================================================================
    # STATE UPDATES (Called by Controller)
    # ========================================================================

    def set_solving(self, is_solving: bool) -> None:
        """Update UI when solving starts/stops."""
        self.is_solving = is_solving
        self.solve_button.configure(state="disabled" if is_solving else "normal")
        self.file_button.configure(state="disabled" if is_solving else "normal")

    def update_status(self, status: str, color: str = "black") -> None:
        """Update status display."""
        self.status_label.configure(text=status, text_color=color)

    def update_stats(self, stats: Dict[str, Any]) -> None:
        """
        Update solver stats display.

        Args:
            stats: Dict with stats keys/values
        """
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", "end")

        for key, value in stats.items():
            self.stats_text.insert("end", f"{key}: {value}\n")

        self.stats_text.configure(state="disabled")

    def set_grid_size(self, size: int) -> None:
        """Programmatically set grid size."""
        if 4 <= size <= 9:
            self.size_var.set(size)
            self.current_size = size

    def get_solver_type(self) -> SolverType:
        """Get currently selected solver type."""
        return self.current_algorithm

    def get_grid_size(self) -> int:
        """Get currently selected grid size."""
        return self.current_size
