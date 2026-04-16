import argparse
import os
from src.utils.parser import load_puzzle_file, save_solution, format_board

# Import solvers
from src.solvers.backtracking import BacktrackingSolver
from src.solvers.forward_chaining import forward_chaining_solver
from src.models.kb import KnowledgeBase
from src.logic.grounding import ground_axioms
# from src.solvers.a_star import AStarSolver

def main():
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
        print("Grounding axioms...")
        ground_axioms(kb, board)
        solution_state = forward_chaining_solver(initial_state, kb)
        solution_grid = solution_state.board if solution_state else None
        solve_time = 0.0  # Forward chaining doesn't track timing
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

if __name__ == "__main__":
    main()
