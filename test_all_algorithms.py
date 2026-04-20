"""
Comprehensive test showing all 3 algorithms can solve Futoshiki puzzles.
"""

import sys
from pathlib import Path
import time

src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.utils.parser import load_puzzle_file
from src.solvers.backtracking import BacktrackingSolver
from src.solvers.forward_chaining import forward_chaining_solver
from src.solvers.a_star import a_star_solver
from src.models.kb import KnowledgeBase
from src.logic.grounding import ground_axioms

def test_all_solvers():
    """Test all 3 algorithms on a 4x4 puzzle."""
    
    print("="*70)
    print("FUTOSHIKI SOLVER - 3 ALGORITHM TEST")
    print("="*70)
    
    # Load puzzle
    board, initial_state = load_puzzle_file("inputs/4x4_matrix.txt")
    
    print(f"\nPuzzle: 4x4 Futoshiki")
    print(f"Initial values: {sum(1 for row in initial_state.board for val in row if val != 0)}/16 cells")
    print(f"Constraints: {len(board.constraints)}")
    
    # Test 1: Backtracking
    print("\n" + "="*70)
    print("1. BACKTRACKING SOLVER")
    print("="*70)
    solver = BacktrackingSolver()
    start = time.time()
    solution_backtracking = solver.solve(board)
    elapsed = time.time() - start
    
    if solution_backtracking:
        print(f"✓ SOLVED in {elapsed:.4f} seconds")
        print(f"  Nodes visited: {solver.nodes_visited}")
        print(f"  Solution: {solution_backtracking}")
    else:
        print("✗ FAILED to find solution")
        solution_backtracking = None
    
    # Test 2: Forward Chaining
    print("\n" + "="*70)
    print("2. FORWARD CHAINING SOLVER")
    print("="*70)
    kb = KnowledgeBase(board.N)
    ground_axioms(kb, board)
    print(f"Grounded clauses: {len(kb.clauses)}")
    
    start = time.time()
    solution_fc = forward_chaining_solver(initial_state, kb)
    elapsed = time.time() - start
    
    if solution_fc:
        print(f"✓ SOLVED in {elapsed:.4f} seconds")
        print(f"  Solution: {solution_fc.board}")
    else:
        print("✗ FAILED to find solution")
        solution_fc = None
    
    # Test 3: A* Search
    print("\n" + "="*70)
    print("3. A* (A-STAR) SOLVER")
    print("="*70)
    
    start = time.time()
    solution_astar = a_star_solver(initial_state, board, "advanced")
    elapsed = time.time() - start
    
    if solution_astar:
        print(f"✓ SOLVED in {elapsed:.4f} seconds")
        print(f"  Solution: {solution_astar.board}")
    else:
        print("✗ FAILED to find solution")
        solution_astar = None
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    solutions = [
        ("Backtracking", solution_backtracking),
        ("Forward Chaining", solution_fc.board if solution_fc else None),
        ("A*", solution_astar.board if solution_astar else None),
    ]
    
    solved_count = sum(1 for _, sol in solutions if sol)
    print(f"\n✓ {solved_count}/3 algorithms found solutions")
    
    for name, solution in solutions:
        status = "✓ SOLVED" if solution else "✗ FAILED"
        print(f"  {name}: {status}")
    
    # Verify all solutions are identical
    if all(sol for _, sol in solutions):
        sol1 = solutions[0][1]
        all_same = all(sol1 == solutions[i][1] for i in range(len(solutions)))
        if all_same:
            print("\n✓ All solutions are identical!")
        else:
            print("\n✗ Solutions differ (this should not happen)")
            for i, (name, sol) in enumerate(solutions):
                if sol != sol1:
                    print(f"  {name} differs from {solutions[0][0]}")
    
    return solved_count == 3

if __name__ == "__main__":
    success = test_all_solvers()
    sys.exit(0 if success else 1)
