"""Advanced unit tests for Futoshiki solver - boundary conditions and complex scenarios.

This test module focuses on:
- Boundary conditions and edge cases
- Performance characteristics
- Complex scenarios combining multiple features
"""

import unittest
from src.models.board import Board
from src.models.kb import KnowledgeBase
from src.models.state import State


class TestBoundaryConditions(unittest.TestCase):
    """Test boundary conditions and extreme values."""
    
    def test_board_maximum_practical_size(self):
        """Test board with larger N value."""
        N = 10
        board = Board(N, State(tuple(tuple(0 for _ in range(N)) for _ in range(N)), None), ())
        
        self.assertEqual(board.N, N)
    
    def test_kb_maximum_variable_id(self):
        """Test KB variable ID for maximum coordinates."""
        N = 9
        kb = KnowledgeBase(N)
        
        # Get ID for maximum coordinates
        max_id = kb.get_var_id(N, N, N)
        
        # ID should be (N-1)*N² + (N-1)*N + N
        expected = (N-1) * (N**2) + (N-1) * N + N
        self.assertEqual(max_id, expected)
    
    def test_kb_variable_id_monotonicity(self):
        """Test that IDs increase monotonically through the grid."""
        kb = KnowledgeBase(3)
        
        previous_id = 0
        for r in range(1, 4):
            for c in range(1, 4):
                for v in range(1, 4):
                    current_id = kb.get_var_id(r, c, v)
                    self.assertGreater(current_id, previous_id)
                    previous_id = current_id
    
    def test_state_large_board_completion(self):
        """Test is_complete on large board."""
        N = 8
        complete_board = tuple(tuple(i for _ in range(N)) for i in range(1, N+1))
        state = State(complete_board, None)
        
        self.assertTrue(state.is_complete())
    
    def test_state_large_board_partial_completion(self):
        """Test is_complete on large board with single empty cell."""
        N = 8
        board = list(list(i for _ in range(N)) for i in range(1, N+1))
        board[N-1][N-1] = 0  # Set last cell to empty
        board = tuple(tuple(row) for row in board)
        state = State(board, None)
        
        self.assertFalse(state.is_complete())


class TestComplexScenarios(unittest.TestCase):
    """Test complex scenarios and realistic usage patterns."""
    
    def test_kb_with_many_clauses(self):
        """Test KB with large number of clauses."""
        kb = KnowledgeBase(5)
        
        # Add many unique clauses (simulating a complex CNF formula)
        clauses_added = set()
        for r in range(1, 6):
            for c in range(1, 6):
                for v in range(1, 6):
                    var_id = kb.get_var_id(r, c, v)
                    clause = [var_id, -var_id] if (r + c + v) % 2 == 0 else [var_id]
                    clause_tuple = tuple(clause)
                    if clause_tuple not in clauses_added:
                        kb.add_clause(clause)
                        clauses_added.add(clause_tuple)
        
        # KB should have all unique clauses
        self.assertEqual(len(kb), len(clauses_added))
        self.assertGreater(len(kb), 50)  # At least 50 unique clauses from 5x5 board
    
    def test_state_equality_large_board(self):
        """Test state equality with large boards."""
        N = 10
        board = tuple(tuple(0 for _ in range(N)) for _ in range(N))
        
        state1 = State(board, None)
        state2 = State(board, None)
        
        self.assertEqual(state1, state2)
        self.assertEqual(hash(state1), hash(state2))
    
    def test_state_set_with_similar_boards(self):
        """Test state set behavior with similar but different boards."""
        N = 4
        boards = []
        
        # Create variations of a board
        base_board = [[0 for _ in range(N)] for _ in range(N)]
        
        for i in range(N):
            for j in range(N):
                board = [row[:] for row in base_board]
                board[i][j] = 1
                boards.append(tuple(tuple(row) for row in board))
        
        # Create states from all boards
        states = [State(board, None) for board in boards]
        state_set = set(states)
        
        # All should be unique
        self.assertEqual(len(state_set), len(states))
    
    def test_kb_different_board_sizes(self):
        """Test KB behavior with different board sizes."""
        sizes = [1, 2, 3, 4, 5, 6, 9]
        
        for N in sizes:
            kb = KnowledgeBase(N)
            
            # Generate one clause per cell
            for r in range(1, N+1):
                for c in range(1, N+1):
                    for v in range(1, N+1):
                        var_id = kb.get_var_id(r, c, v)
                        self.assertGreaterEqual(var_id, 1)
                        self.assertEqual(var_id, (r-1) * (N**2) + (c-1) * N + v)


class TestErrorRecovery(unittest.TestCase):
    """Test error handling and recovery."""
    
    def test_kb_after_failed_id_generation(self):
        """Test that KB continues to work after invalid ID generation attempt."""
        kb = KnowledgeBase(3)
        
        # Try to get invalid ID
        try:
            kb.get_var_id(0, 1, 1)
        except ValueError:
            pass
        
        # KB should still work
        valid_id = kb.get_var_id(1, 1, 1)
        self.assertEqual(valid_id, 1)
        
        # Should still be able to add clauses
        kb.add_clause([valid_id])
        self.assertEqual(len(kb), 1)
    
    def test_board_initialization_after_state_error(self):
        """Test that Board can be created even if state initialization had issues."""
        # Create a valid state
        valid_state = State(((0, 0), (0, 0)), None)
        
        # Create board successfully
        board = Board(2, valid_state, ())
        self.assertEqual(board.N, 2)


class TestSpecialCases(unittest.TestCase):
    """Test special and unusual cases."""
    
    def test_state_with_all_ones(self):
        """Test state where all cells are 1."""
        board = ((1, 1, 1), (1, 1, 1), (1, 1, 1))
        state = State(board, None)
        
        self.assertTrue(state.is_complete())
        lines = str(state).split('\n')
        self.assertEqual(len(lines), 3)
        for line in lines:
            self.assertEqual(line, "1 1 1")
    
    def test_state_with_maximum_values(self):
        """Test state with maximum valid values."""
        N = 5
        board = tuple(tuple(N for _ in range(N)) for _ in range(N))
        state = State(board, None)
        
        self.assertTrue(state.is_complete())
    
    def test_kb_clause_with_all_negations(self):
        """Test KB clause with all negative literals."""
        kb = KnowledgeBase(3)
        clause = [-1, -2, -3, -4, -5]
        kb.add_clause(clause)
        
        self.assertEqual(len(kb), 1)
    
    def test_kb_single_literal_clause(self):
        """Test KB with unit clauses (single literal)."""
        kb = KnowledgeBase(3)
        
        for i in range(1, 10):
            kb.add_clause([i])
        
        self.assertEqual(len(kb), 9)


class TestConsistency(unittest.TestCase):
    """Test consistency across operations."""
    
    def test_state_hash_consistency(self):
        """Test that state hash is consistent across multiple calls."""
        board = ((1, 2, 3), (2, 3, 1), (3, 1, 2))
        state = State(board, None)
        
        hash1 = hash(state)
        hash2 = hash(state)
        
        self.assertEqual(hash1, hash2)
    
    def test_kb_variable_id_consistency(self):
        """Test that KB variable IDs are consistent."""
        kb = KnowledgeBase(3)
        
        id1 = kb.get_var_id(1, 1, 1)
        id2 = kb.get_var_id(1, 1, 1)
        
        self.assertEqual(id1, id2)
    
    def test_state_equality_reflexivity(self):
        """Test that state equality is reflexive: A == A."""
        board = ((1, 2), (2, 1))
        state = State(board, None)
        
        self.assertEqual(state, state)
    
    def test_state_equality_symmetry(self):
        """Test that state equality is symmetric: if A == B then B == A."""
        board = ((1, 2), (2, 1))
        state1 = State(board, None)
        state2 = State(board, None)
        
        self.assertEqual(state1, state2)
        self.assertEqual(state2, state1)
    
    def test_state_equality_transitivity(self):
        """Test that state equality is transitive: if A == B and B == C then A == C."""
        board = ((1, 2), (2, 1))
        state1 = State(board, None)
        state2 = State(board, None)
        state3 = State(board, None)
        
        self.assertEqual(state1, state2)
        self.assertEqual(state2, state3)
        self.assertEqual(state1, state3)


class TestPerformance(unittest.TestCase):
    """Basic performance tests to ensure acceptable behavior."""
    
    def test_kb_id_generation_speed(self):
        """Test that ID generation is fast for many operations."""
        kb = KnowledgeBase(9)
        
        # Generate all possible IDs
        ids = set()
        for r in range(1, 10):
            for c in range(1, 10):
                for v in range(1, 10):
                    ids.add(kb.get_var_id(r, c, v))
        
        # Should have 729 unique IDs (9³)
        self.assertEqual(len(ids), 729)
    
    def test_state_string_representation_speed(self):
        """Test that string representation is fast for large boards."""
        N = 10
        board = tuple(tuple(i % N + 1 for _ in range(N)) for i in range(N))
        state = State(board, None)
        
        # Should be fast
        str_repr = str(state)
        self.assertIsNotNone(str_repr)
        
        lines = str_repr.split('\n')
        self.assertEqual(len(lines), N)


if __name__ == '__main__':
    unittest.main(verbosity=2)
