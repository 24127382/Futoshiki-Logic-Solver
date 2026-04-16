"""Command-line entrypoint for the Futoshiki solver."""

from __future__ import annotations

import argparse
import glob
from typing import Optional

from benchmark import benchmark_solver, print_summary
from src.logic.grounding import ground_axioms
from src.models.kb import KnowledgeBase
from src.solvers.a_star import a_star_solver
from src.solvers.forward_chaining import forward_chaining_solver
from src.utils.parser import format_board, load_puzzle_file, save_solution


def run_solve(
    input_file: str,
    output_file: Optional[str] = None,
    solver_name: str = "forward_chaining",
    heuristic_name: str = "advanced",
) -> int:
    """Solve one puzzle using the default solver pipeline."""
    board, initial_state = load_puzzle_file(input_file)

    print(f"Loaded puzzle: {input_file}")
    print(f"Board size: {board.N}x{board.N}")
    print(f"Constraints: {len(board.constraints)}")
    print(format_board(initial_state.board, "Initial State"))

    if solver_name == "forward_chaining":
        kb = KnowledgeBase(board.N)
        ground_axioms(kb, board)
        print(f"\nGrounded clauses: {len(kb.clauses)}")
        solution = forward_chaining_solver(initial_state, kb)
    elif solver_name == "a_star":
        print(f"\nUsing A* solver (heuristic={heuristic_name})...")
        solution = a_star_solver(initial_state, board, heuristic_name)
    else:
        raise ValueError(f"Unsupported solver: {solver_name}")

    if solution is None:
        print("\nNo solution found.")
        return 2

    print(format_board(solution.board, "Solution"))
    print("\nPuzzle solved.")

    if output_file:
        save_solution(solution.board, output_file)
        print(f"Saved solution to: {output_file}")

    return 0


def run_benchmark(pattern: str) -> int:
    """Run benchmark across puzzle files matching pattern."""
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"No puzzle files matched: {pattern}")
        return 1

    all_metrics = {}
    for puzzle_file in files:
        try:
            all_metrics[puzzle_file] = benchmark_solver(puzzle_file)
        except Exception as exc:  # pragma: no cover - benchmark errors are reported per file
            print(f"Benchmark failed for {puzzle_file}: {exc}")

    if all_metrics:
        print_summary(all_metrics)
        return 0

    return 1


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for solver and benchmark workflows."""
    parser = argparse.ArgumentParser(description="Futoshiki solver")
    subparsers = parser.add_subparsers(dest="command")

    solve_parser = subparsers.add_parser("solve", help="Solve one puzzle file")
    solve_parser.add_argument("--input", required=True, help="Path to puzzle input file")
    solve_parser.add_argument("--output", help="Optional path to write solved board")
    solve_parser.add_argument(
        "--solver",
        default="forward_chaining",
        choices=["forward_chaining", "a_star"],
        help="Solver to run (default: forward_chaining)",
    )
    solve_parser.add_argument(
        "--heuristic",
        default="advanced",
        choices=[
            "advanced",
            "combined",
            "domain_width",
            "remaining_cells",
            "constraint_violations",
            "missing_values",
            "sum_remaining_values",
            "inequality_violations",
            "inequality_slack",
        ],
        help="Heuristic for A* (ignored by forward_chaining)",
    )

    bench_parser = subparsers.add_parser("benchmark", help="Benchmark one or more puzzle files")
    bench_parser.add_argument(
        "--pattern",
        default="inputs/*.txt",
        help="Glob pattern for puzzle files (default: inputs/*.txt)",
    )

    return parser


def main() -> int:
    """Program entrypoint."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "solve":
        return run_solve(args.input, args.output, args.solver, args.heuristic)
    if args.command == "benchmark":
        return run_benchmark(args.pattern)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
