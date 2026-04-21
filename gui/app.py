"""
Main Application Module: Futoshiki Solver GUI
==============================================
Tkinter-based GUI for solving Futoshiki puzzles.

Architecture:
- Sidebar (left): Controls, file loader, algorithm selector
- BoardFrame (right): 4x9 grid display
- Controller: Mediates between GUI and solvers
- Bridge: Translates data formats

Data Flow:
1. User loads file → Parser reads it → Sidebar updates
2. User clicks "Solve" → Controller._solve_worker() runs in thread
3. Solver finishes → Controller calls update_callback()
4. GUI updates BoardFrame with solution

Design Pattern: MVC (Model-View-Controller)
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import sys
from pathlib import Path

# Add src/ to path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from gui.sidebar import Sidebar
from gui.board_frame import BoardFrame
from gui.controller import FutoshikiController, SolverType


class FutoshikiApp(ctk.CTk):
    """
    Main application window.

    Layout:
    ┌─────────────────┬──────────────────────────┐
    │                 │                          │
    │   Sidebar       │   Board Frame            │
    │  (Controls)     │  (20x20 Grid)            │
    │                 │                          │
    └─────────────────┴──────────────────────────┘

    Responsibilities:
    - Initialize and layout tkinter window
    - Create controller, sidebar, board_frame
    - Wire up callbacks between components
    - Show status/error messages
    - Manage async operations (loading overlay)
    """

    def __init__(self):
        """Initialize the application."""
        super().__init__()

        # Window setup
        self.title("Futoshiki Solver")
        self.geometry("1200x700")
        self.minsize(900, 500)

        # Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create main controller
        self.controller = FutoshikiController(
            update_callback=self._on_controller_update
        )

        # Create UI components
        self._create_widgets()

    # ========================================================================
    # WIDGET CREATION
    # ========================================================================

    def _create_widgets(self) -> None:
        """Create and layout all UI components."""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True)

        # Create sidebar (left)
        self.sidebar = Sidebar(
            main_frame,
            on_solve_click=self._on_solve_click,
            fg_color="#1a1a2e",
            width=300
        )
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)

        # Create board frame (right)
        board_container = ctk.CTkFrame(main_frame)
        board_container.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Label for board
        ctk.CTkLabel(
            board_container,
            text="Futoshiki Grid",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        # The actual board (starts with 4x4)
        self.board_frame = BoardFrame(
            board_container,
            size=4,
            cell_width=50,
            constraint_width=35,
            fg_color="#0f0f1e"
        )
        self.board_frame.pack(fill="both", expand=True)

        # Wire up sidebar callbacks
        self.sidebar.on_file_load = self._on_file_load
        self.sidebar.on_size_change = self._on_size_change
        self.sidebar.on_clear_click = self._on_clear_click
        self.sidebar.on_constraint_mode_toggle = self._on_constraint_mode_toggle
    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================

    def _on_solve_click(self, size: int, algorithm: SolverType, timeout: int) -> None:
        """
        Handle Solve button click from sidebar.
        """
        # Resize board if needed
        if self.board_frame.get_size() != size:
            self.board_frame.resize(size)

        # Get current matrix and constraints from board
        gui_matrix = self.board_frame.get_matrix()
        gui_constraints = self.board_frame.get_constraints()

        # ==========================================
        # NEW VALIDATION: Prevent solving empty grid
        # ==========================================
        is_matrix_empty = all(cell == "" for row in gui_matrix for cell in row)
        has_no_constraints = len(gui_constraints) == 0

        if is_matrix_empty and has_no_constraints:
            messagebox.showwarning(
                "Empty Board",
                "The grid is completely empty!\n\nPlease load a puzzle file or enter some numbers/constraints before solving."
            )
            return  # Stop execution here
        # ==========================================

        # Set timeout on controller
        self.controller.set_timeout(timeout)

        # Update sidebar UI
        self.sidebar.set_solving(True)
        self.sidebar.update_status("Solving...", color="#ffaa00")

        # Call controller (non-blocking)
        self.controller.handle_solve_request(
            gui_matrix,
            gui_constraints,
            size,
            algorithm
        )

    def _on_file_load(self, filepath: str) -> None:
        """Handle file load from sidebar."""
        try:
            # 1. Ask controller to parse and format the file
            matrix, constraints, size = self.controller.load_puzzle_from_file(filepath)

            # 2. Update the Sidebar radio buttons
            self.sidebar.set_grid_size(size)

            # 3. Update the BoardFrame (Resizes grid, inserts numbers, draws < > signs)
            self.board_frame.resize(size)
            self.board_frame.set_matrix(matrix)
            self.board_frame.set_constraints(constraints)

            self.sidebar.update_status(f"Loaded: {filepath.split('/')[-1]}", color="#00cc66")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

    def _on_size_change(self, new_size: int) -> None:
        """
        Handle grid size change from sidebar.

        Args:
            new_size: New grid size (4-9)
        """
        try:
            self.board_frame.resize(new_size)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to resize grid:\n{str(e)}")

    def _on_clear_click(self) -> None:
        """Handle clear grid request from sidebar."""
        # 1. Re-enable typing FIRST! Tkinter cannot delete text from disabled entries.
        self.board_frame.enable_editing()

        # 2. Clear the numbers and < > signs from the board
        self.board_frame.clear_grid()

        # 3. Reset the sidebar text
        self.sidebar.update_status("Ready", color="#00cc66")
        self.sidebar.update_stats({})
        self.sidebar.file_label.configure(text="No file loaded")

    def _on_constraint_mode_toggle(self, enabled: bool) -> None:
        """
        Handle constraint mode toggle from sidebar.
        
        Args:
            enabled: True to enable constraint mode, False for value input mode
        """
        self.board_frame.set_constraint_mode(enabled)
        mode_text = "✏️ Constraint Mode: ACTIVE" if enabled else "Value Input Mode"
        self.sidebar.update_status(mode_text, color="#ffaa00" if enabled else "#00cc66")

    # ========================================================================
    # CONTROLLER CALLBACKS (What Controller calls back to GUI with)
    # ========================================================================

    def _on_controller_update(self, status: str, data: dict = None) -> None:
        """
        Callback from controller with status updates.

        Args:
            status: 'solving', 'success', 'error', 'unsolvable'
            data: Additional data (solution, stats, etc.)

        This runs in the controller's background thread, so we must
        use self.after() to update UI safely from the main thread.
        """
        data = data or {}

        # Schedule UI update in main thread
        self.after(0, self._update_ui_from_result, status, data)

    def _update_ui_from_result(self, status: str, data: dict) -> None:
        """Update UI with result from solver (runs in main thread)."""
        self.sidebar.set_solving(False)

        # ALWAYS update the board if a matrix is provided (shows partial progress!)
        if data.get('solution'):
            self.board_frame.set_matrix(data['solution'])

        if status == 'solving':
            self.sidebar.update_status("Solving...", color="#ffaa00")

        elif status == 'success':
            self.board_frame.disable_editing()
            stats = data.get('stats', {})
            self.sidebar.update_stats(stats)
            self.sidebar.update_status("✓ Solved!", color="#00cc66")
            messagebox.showinfo("Success", data.get('message', "Puzzle solved!"))

        elif status == 'unsolvable':
            self.sidebar.update_status("✗ Unsolvable / Partial", color="#cc0000")
            stats = data.get('stats', {})
            self.sidebar.update_stats(stats)
            messagebox.showwarning("Unsolvable", data.get('message', "This puzzle cannot be solved completely."))

        elif status == 'not_implemented':
            self.sidebar.update_status("⚠️ Not In Service", color="#ffaa00")
            messagebox.showwarning("Not Implemented", data.get('message', "This algorithm is not implemented yet."))

        elif status == 'error':
            message = data.get('message', 'Unknown error')
            self.sidebar.update_status(f"✗ Error", color="#cc0000")
            messagebox.showerror("Error", f"Solve failed:\n{message}")

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def show_loading_overlay(self, show: bool = True) -> None:
        """
        Show/hide a loading overlay to indicate busy state.

        TODO: Implement visual loading indicator
        - Could be a semi-transparent overlay with "Solving..." text
        - Or just disable all buttons (already doing this in sidebar.set_solving)
        """
        pass

    def run(self) -> None:
        """Start the application."""
        self.mainloop()


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Create and run the application."""
    app = FutoshikiApp()
    app.run()


if __name__ == "__main__":
    main()
