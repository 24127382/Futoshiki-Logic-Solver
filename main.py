"""
Futoshiki Solver - Main Entry Point
====================================
Supports two modes:
1. GUI mode (default): Launch tkinter GUI for interactive solving
2. CLI mode (--cli flag): Run puzzles from command line

Usage:
    python main.py                          # Launch GUI
    python main.py --cli --input puzzle.txt --solver backtracking
"""

import argparse
import os
import sys
from pathlib import Path

# Add src/ and gui/ to path
src_path = str(Path(__file__).parent / "src")
gui_path = str(Path(__file__).parent / "gui")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
if gui_path not in sys.path:
    sys.path.insert(0, gui_path)

from src.utils.parser import load_puzzle_file, save_solution, format_board

# Import solvers
from src.solvers.backtracking import BacktrackingSolver
from src.solvers.forward_chaining import forward_chaining_solver
from src.solvers.backward_chaining import backward_chaining_solver
from src.models.kb import KnowledgeBase
from src.logic.grounding import ground_axioms
# from src.solvers.a_star import AStarSolver


def main_gui():
    """Launch the tkinter GUI application."""
    from gui.app import FutoshikiApp
    app = FutoshikiApp()
    app.run()


def main_cli():
    """Run CLI mode (backward compatible with original main.py)."""
    parser = argparse.ArgumentParser(description="Futoshiki Solver AI Sandbox")
    parser.add_argument("--input", type=str, required=True, help="Path to input puzzle file")
    parser.add_argument("--solver", type=str, required=True, choices=['backtracking', 'a_star', 'forward_chaining', 'backward_chaining'], help="Solver algorithm to use")
    parser.add_argument("--output", type=str, default="outputs", help="Directory or file path to save the solution")
    parser.add_argument("--verbose", action="store_true", help="Enable detailed logging")

    args = parser.parse_args()

    # 1. Load the puzzle
    try:
        board, initial_state = load_puzzle_file(args.input)
        if args.verbose:
            print(f"Loaded puzzle from {args.input}")
            print(format_board(initial_state.board, title="Initial State"))
    except Exception as e:
        print(f"Error loading puzzle: {e}")
        return

    # 2. Select and initialize the solver
    if args.solver == 'backtracking':
        solver = BacktrackingSolver()
        print(f"\nSolving with {args.solver}...")
        solution_grid = solver.solve(board)
        solve_time = solver.solve_time
        nodes_visited = solver.nodes_visited
        
    elif args.solver == 'forward_chaining':
        print(f"\nSolving with {args.solver}...")
        kb = KnowledgeBase(board.N)
        ground_axioms(kb, board)
        print(f"\nGrounded clauses: {len(kb.clauses)}")
        solution_state = forward_chaining_solver(initial_state, kb)
        solution_grid = solution_state.board if solution_state else None
        solve_time = 0  # Forward chaining doesn't track time
        nodes_visited = 0
    elif args.solver == 'a_star':
        from src.solvers.a_star import a_star_solver
        print(f"\nUsing A* solver...")
        solution_state = a_star_solver(initial_state, board, "advanced")
        solution_grid = solution_state.board if solution_state else None
        solve_time = 0
        nodes_visited = 0
    elif args.solver == 'backward_chaining':
        print(f"\nSolving with {args.solver}...")
        kb = KnowledgeBase(board.N)
        ground_axioms(kb, board)
        print(f"\nGrounded clauses: {len(kb.clauses)}")
        solution_state = backward_chaining_solver(initial_state, kb)
        solution_grid = solution_state.board if solution_state else None
        solve_time = 0
        nodes_visited = 0
    else:
        print(f"Solver '{args.solver}' is not yet implemented.")
        return

    # 3. Handle Output
    if solution_grid:
        print(f"\nSolution found in {solve_time:.4f} seconds!")
        if nodes_visited > 0:
            print(f"Nodes visited: {nodes_visited}")

        if args.verbose:
            print(format_board(solution_grid, title="Solved State"))

        # Prepare output directory/filename
        if os.path.isdir(args.output) or not args.output.endswith('.txt'):
            os.makedirs(args.output, exist_ok=True)
            base_name = os.path.basename(args.input).replace('.txt', '_solution.txt')
            output_path = os.path.join(args.output, base_name)
        else:
            output_path = args.output

        # Save it
        save_solution(solution_grid, output_path)
        print(f"Solution saved to {output_path}")
    else:
        print("\nNo solution exists for this puzzle.")


def main():
    """
    Main entry point dispatcher.
    
    Checks for --cli flag:
    - With --cli: Run in CLI mode (original behavior)
    - Without --cli: Launch tkinter GUI
    """
    # Check if --cli flag is present
    if '--cli' in sys.argv:
        # Remove --cli from argv so argparse doesn't complain
        sys.argv.remove('--cli')
        main_cli()
    else:
        # Launch GUI mode
        main_gui()


if __name__ == "__main__":
    raise SystemExit(main())
