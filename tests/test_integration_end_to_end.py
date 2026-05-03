"""Integration tests for parser -> grounding -> solver pipeline."""

import os
import tempfile
import unittest

from src.logic.grounding import ground_axioms
from src.models.kb import KnowledgeBase
from src.models.state import State
from src.solvers.forward_chaining import forward_chaining_solver
from src.utils.parser import load_puzzle_file


class TestEndToEndPipeline(unittest.TestCase):
    """End-to-end tests for puzzle loading and solving workflow."""

    def test_parser_supports_canonical_quintuple_constraints(self):
        content = "\n".join([
            "3",
            "0 0 0",
            "0 0 0",
            "0 0 0",
            "0 0 < 0 1 1 1 > 2 1",
        ])

        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            board, _ = load_puzzle_file(tmp_path)
        finally:
            os.remove(tmp_path)

        self.assertEqual(len(board.constraints), 2)
        self.assertEqual(board.constraints[0], (1, 1, "<", 1, 2))
        self.assertEqual(board.constraints[1], (2, 2, ">", 3, 2))

    def test_parser_legacy_triplets_are_backward_compatible(self):
        content = "\n".join([
            "3",
            "0 0 0",
            "0 0 0",
            "0 0 0",
            "0 0 < 1 1 >",
        ])

        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            board, _ = load_puzzle_file(tmp_path)
        finally:
            os.remove(tmp_path)

        self.assertEqual(board.constraints, ((1, 1, "<", 1, 2), (2, 2, ">", 2, 3)))

    def test_grounding_adds_inequality_clauses(self):
        content = "\n".join([
            "3",
            "0 0 0",
            "0 0 0",
            "0 0 0",
            "0 0 < 0 1",
        ])

        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            board, _ = load_puzzle_file(tmp_path)
        finally:
            os.remove(tmp_path)

        kb = KnowledgeBase(board.N)
        ground_axioms(kb, board)

        # For (1,1) < (1,2), optimized unit clauses must exist.
        self.assertIn((-kb.get_var_id(1, 1, 3),), kb.clauses)
        self.assertIn((-kb.get_var_id(1, 2, 1),), kb.clauses)

    def test_full_pipeline_smoke_test(self):
        puzzle_path = os.path.join(os.path.dirname(__file__), "..", "inputs", "puzzle_3x3_simple.txt")
        puzzle_path = os.path.abspath(puzzle_path)

        board, initial_state = load_puzzle_file(puzzle_path)
        kb = KnowledgeBase(board.N)
        ground_axioms(kb, board)
        solution = forward_chaining_solver(initial_state, kb)

        self.assertTrue(solution is None or isinstance(solution, State))


if __name__ == "__main__":
    unittest.main()
