import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import sys, os
from pathlib import Path

src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from gui.sidebar import Sidebar
from gui.board_frame import BoardFrame
from gui.controller import FutoshikiController, SolverType

class FutoshikiApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Futoshiki Solver")
        self.geometry("1200x700")
        self.minsize(900, 500)

        # SWITCH TO LIGHT THEME
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.controller = FutoshikiController(update_callback=self._on_controller_update)
        self._create_widgets()

    def _create_widgets(self) -> None:
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True)

        self.sidebar = Sidebar(main_frame, on_solve_click=self._on_solve_click, width=300)
        self.sidebar.pack(side="left", fill="y")

        board_container = ctk.CTkFrame(main_frame)
        board_container.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(board_container, text="Futoshiki Grid", font=("Arial", 14, "bold")).pack(pady=5)

        self.board_frame = BoardFrame(board_container, size=4, cell_width=50, constraint_width=35)
        self.board_frame.pack(fill="both", expand=True)

        self.sidebar.on_file_load = self._on_file_load
        self.sidebar.on_size_change = self._on_size_change
        self.sidebar.on_clear_click = self._on_clear_click
        self.sidebar.on_constraint_mode_toggle = self._on_constraint_mode_toggle

    def _on_solve_click(self, size: int, algorithm: SolverType, timeout: int) -> None:
        if self.board_frame.get_size() != size:
            self.board_frame.resize(size)
        gui_matrix = self.board_frame.get_matrix()
        gui_constraints = self.board_frame.get_constraints()

        is_matrix_empty = all(cell == "" for row in gui_matrix for cell in row)
        if is_matrix_empty and len(gui_constraints) == 0:
            messagebox.showwarning("Empty Board", "Please load a puzzle or enter numbers before solving.")
            return

        self.controller.set_timeout(timeout)
        self.sidebar.set_solving(True)
        self.sidebar.update_status("Solving...", color="darkorange")
        self.controller.handle_solve_request(gui_matrix, gui_constraints, size, algorithm)

    def _on_file_load(self, filepath: str) -> None:
        try:
            self.board_frame.enable_editing()
            self.board_frame.clear_grid()
            self.sidebar.update_stats({})
            matrix, constraints, size = self.controller.load_puzzle_from_file(filepath)
            self.sidebar.set_grid_size(size)
            self.board_frame.resize(size)
            self.board_frame.set_matrix(matrix)
            self.board_frame.set_constraints(constraints)
            self.sidebar.update_status(f"Loaded: {os.path.basename(filepath)}", color="green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

    def _on_size_change(self, new_size: int) -> None:
        try: self.board_frame.resize(new_size)
        except Exception as e: messagebox.showerror("Error", f"Failed to resize:\n{str(e)}")

    def _on_clear_click(self) -> None:
        self.board_frame.enable_editing()
        self.board_frame.clear_grid()
        self.sidebar.update_status("Ready", color="green")
        self.sidebar.update_stats({})
        self.sidebar.file_label.configure(text="No file loaded")

    def _on_constraint_mode_toggle(self, enabled: bool) -> None:
        self.board_frame.set_constraint_mode(enabled)
        mode_text = "✏️ Constraint Mode: ACTIVE" if enabled else "Value Input Mode"
        self.sidebar.update_status(mode_text, color="darkorange" if enabled else "green")

    def _on_controller_update(self, status: str, data: dict = None) -> None:
        self.after(0, self._update_ui_from_result, status, data or {})

    def _update_ui_from_result(self, status: str, data: dict) -> None:
        self.sidebar.set_solving(False)
        if data.get('solution'):
            self.board_frame.set_matrix(data['solution'])

        if status == 'solving':
            self.sidebar.update_status("Solving...", color="darkorange")
        elif status == 'success':
            self.board_frame.disable_editing()
            self.sidebar.update_stats(data.get('stats', {}))
            self.sidebar.update_status("✓ Solved!", color="green")
            messagebox.showinfo("Success", data.get('message', "Puzzle solved!"))
        elif status == 'unsolvable':
            self.sidebar.update_status("✗ Unsolvable / Partial", color="red")
            self.sidebar.update_stats(data.get('stats', {}))
            messagebox.showwarning("Unsolvable", data.get('message', "Puzzle cannot be solved completely."))
        elif status == 'not_implemented':
            self.sidebar.update_status("⚠️ Not In Service", color="darkorange")
            messagebox.showwarning("Not Implemented", data.get('message', "Algorithm not implemented."))
        elif status == 'error':
            self.sidebar.update_status("✗ Error/Timeout", color="red")
            messagebox.showerror("Error", f"Solve failed:\n{data.get('message', 'Unknown error')}")

    def run(self) -> None:
        self.mainloop()

def main():
    FutoshikiApp().run()

if __name__ == "__main__":
    main()
