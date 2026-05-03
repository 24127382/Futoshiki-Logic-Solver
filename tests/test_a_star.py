"""Unit tests for A* solver."""

import unittest

from src.models.board import Board
from src.models.state import State
from src.solvers.a_star import a_star_solver


class TestAStarSolver(unittest.TestCase):
    """Behavior tests for A* solver."""

    def test_a_star_solves_simple_2x2(self):
        initial = State(((1, 0), (0, 0)), None)
        board = Board(2, initial, ())

        solution = a_star_solver(initial, board)

        self.assertIsNotNone(solution)
        if solution is None:
            return

        self.assertTrue(solution.is_complete())
        # 2x2 Latin-square constraints
        self.assertEqual(set(solution.board[0]), {1, 2})
        self.assertEqual(set(solution.board[1]), {1, 2})
        self.assertEqual({solution.board[0][0], solution.board[1][0]}, {1, 2})
        self.assertEqual({solution.board[0][1], solution.board[1][1]}, {1, 2})

    def test_a_star_respects_inequality_constraint(self):
        initial = State(((1, 0), (0, 0)), None)
        # (0,0) < (0,1) forces first row to be (1,2) [0-based indexing from parser]
        constraints = ((0, 0, "<", 0, 1),)
        board = Board(2, initial, constraints)

        solution = a_star_solver(initial, board)

        self.assertIsNotNone(solution)
        if solution is None:
            return

        self.assertEqual(solution.board[0][0], 1)
        self.assertEqual(solution.board[0][1], 2)
        self.assertLess(solution.board[0][0], solution.board[0][1])

    def test_a_star_returns_none_for_invalid_initial_state(self):
        # Duplicate value in first row already violates row uniqueness
        initial = State(((1, 1), (0, 0)), None)
        board = Board(2, initial, ())

        solution = a_star_solver(initial, board)
        self.assertIsNone(solution)


if __name__ == "__main__":
    unittest.main()
