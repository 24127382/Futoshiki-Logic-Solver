"""Unit tests for Futoshiki heuristics."""

import unittest

from src.models.board import Board
from src.models.state import State
from src.utils.heuristic import (
    get_heuristic,
    h_domain_width,
    h_futoshiki_advanced,
    h_inequality_slack,
    h_inequality_violations,
)


class TestHeuristicFunctions(unittest.TestCase):
    """Tests for domain-aware and inequality-aware heuristics."""

    def test_inequality_violations_supports_canonical_constraint(self):
        state = State(((2, 1), (0, 0)), None)
        board = Board(2, state, ((1, 1, "<", 1, 2),))

        self.assertEqual(h_inequality_violations(state, board), 1)

    def test_inequality_violations_supports_legacy_constraint(self):
        state = State(((2, 1), (0, 0)), None)
        board = Board(2, state, ((1, 1, "<"),))

        self.assertEqual(h_inequality_violations(state, board), 1)

    def test_domain_width_penalizes_dead_end(self):
        # Cell (2,2) has no legal value under row/column constraints.
        state = State(((1, 2), (1, 0)), None)
        board = Board(2, state, ())

        self.assertGreaterEqual(h_domain_width(state, board), 10**6)

    def test_inequality_slack_positive_for_unresolved_constraint(self):
        state = State(((1, 0), (0, 0)), None)
        board = Board(2, state, ((1, 1, "<", 1, 2),))

        self.assertGreater(h_inequality_slack(state, board), 0)

    def test_get_heuristic_unknown_falls_back_to_advanced(self):
        state = State(((0, 0), (0, 0)), None)
        board = Board(2, state, ())

        fn = get_heuristic("unknown_name")
        self.assertEqual(fn(state, board), h_futoshiki_advanced(state, board))


if __name__ == "__main__":
    unittest.main()
