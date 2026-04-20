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

# Import the new GUI-adapted solvers
from src.solvers.backtracking import BacktrackingSolver
from src.solvers.forward_chaining import ForwardChainingSolver
from gui.bridge import InputData

def main_gui():
    """Launch the tkinter GUI application."""
    from gui.app import FutoshikiApp
    app = FutoshikiApp()
    app.run()

def main_cli():
    """Run CLI mode (adapted for the new OutputData solver contracts)."""
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

    # 2. Package into InputData for our new solvers
    gui_matrix = [list(row) for row in initial_state.board]
    gui_constraints = []
    for r1, c1, op, r2, c2 in board.constraints:
        gui_constraints.append(((r1, c1), (r2, c2), op))

    input_data = InputData(size=board.N, matrix=gui_matrix, constraints=gui_constraints)

    # 3. Select and initialize the solver
    if args.solver == 'backtracking':
        print(f"\nSolving with {args.solver}...")
        solver = BacktrackingSolver()
        output = solver.solve(input_data)

    elif args.solver == 'forward_chaining':
        print(f"\nSolving with {args.solver}...")
        solver = ForwardChainingSolver()
        output = solver.solve(input_data)

    else:
        print(f"Solver '{args.solver}' is not yet implemented.")
        return

    solution_grid = output.solution
    solve_time = output.stats.get('time_ms', 0) / 1000.0

    # 4. Handle Output
    if solution_grid:
        print(f"\nSolution found in {solve_time:.4f} seconds!")

        # Display specific stats based on the solver used
        if 'nodes_visited' in output.stats:
            print(f"Nodes visited: {output.stats['nodes_visited']}")
        elif 'clauses_generated' in output.stats:
            print(f"Clauses generated: {output.stats['clauses_generated']}")

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
        print(f"\nNo solution exists for this puzzle. ({output.message})")


def main():
    """
    Main entry point dispatcher.
    """
    if '--cli' in sys.argv:
        sys.argv.remove('--cli')
        main_cli()
    else:
        main_gui()

if __name__ == "__main__":
    main()
