"""Comprehensive unit tests for Futoshiki solver models.

Tests cover:
- Board initialization and validation
- Knowledge base clause management and ID generation
- State representation and completion checking
"""

import unittest
from src.models.board import Board
from src.models.kb import KnowledgeBase
from src.models.state import State


class TestBoard(unittest.TestCase):
    """Test cases for Board class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple 3x3 initial state
        self.initial_state_3x3 = State(
            ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
            None
        )
        # Create constraints for a simple puzzle
        self.constraints_simple = (
            (0, 0, '<'),  # cell[0][0] < cell[0][1]
            (0, 1, '>'),  # cell[0][1] > cell[0][2]
        )
    
    def test_board_initialization_valid(self):
        """Test valid board initialization."""
        board = Board(3, self.initial_state_3x3, self.constraints_simple)
        
        self.assertEqual(board.N, 3)
        self.assertEqual(board.initial_state, self.initial_state_3x3)
        self.assertEqual(len(board.constraints), 2)
    
    def test_board_initialization_single_cell(self):
        """Test board initialization with N=1."""
        state = State(((0,),), None)
        board = Board(1, state, ())
        
        self.assertEqual(board.N, 1)
        self.assertEqual(len(board.constraints), 0)
    
    def test_board_initialization_large_board(self):
        """Test board initialization with larger board."""
        state = State(tuple(tuple(0 for _ in range(5)) for _ in range(5)), None)
        constraints = ((i, j, '<') for i in range(5) for j in range(4))
        board = Board(5, state, tuple(constraints))
        
        self.assertEqual(board.N, 5)
        self.assertGreater(len(board.constraints), 0)
    
    def test_board_invalid_size_zero(self):
        """Test board initialization fails with N=0."""
        with self.assertRaises(ValueError) as context:
            Board(0, self.initial_state_3x3, self.constraints_simple)
        
        self.assertIn("positive", str(context.exception))
    
    def test_board_invalid_size_negative(self):
        """Test board initialization fails with negative N."""
        with self.assertRaises(ValueError) as context:
            Board(-1, self.initial_state_3x3, self.constraints_simple)
        
        self.assertIn("positive", str(context.exception))
    
    def test_board_empty_constraints(self):
        """Test board with no constraints."""
        board = Board(3, self.initial_state_3x3, ())
        
        self.assertEqual(len(board.constraints), 0)
    
    def test_board_repr(self):
        """Test board string representation."""
        board = Board(3, self.initial_state_3x3, self.constraints_simple)
        repr_str = repr(board)
        
        self.assertIn("Board", repr_str)
        self.assertIn("3", repr_str)
        self.assertIn("2", repr_str)  # 2 constraints
    
    def test_board_str(self):
        """Test board detailed string representation."""
        board = Board(4, self.initial_state_3x3, self.constraints_simple)
        str_repr = str(board)
        
        self.assertIn("Futoshiki", str_repr)
        self.assertIn("4x4", str_repr)
        self.assertIn("2", str_repr)  # 2 constraints


class TestKnowledgeBase(unittest.TestCase):
    """Test cases for KnowledgeBase class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.kb_3x3 = KnowledgeBase(3)
        self.kb_4x4 = KnowledgeBase(4)
    
    def test_kb_initialization(self):
        """Test knowledge base initialization."""
        self.assertEqual(self.kb_3x3.N, 3)
        self.assertEqual(len(self.kb_3x3), 0)
    
    def test_kb_initialization_invalid_zero(self):
        """Test KB initialization fails with N=0."""
        with self.assertRaises(ValueError) as context:
            KnowledgeBase(0)
        
        self.assertIn("positive", str(context.exception))
    
    def test_kb_initialization_invalid_negative(self):
        """Test KB initialization fails with negative N."""
        with self.assertRaises(ValueError) as context:
            KnowledgeBase(-5)
        
        self.assertIn("positive", str(context.exception))
    
    def test_get_var_id_basic(self):
        """Test variable ID generation for basic coordinates."""
        # For 3x3: ID = (r-1) * 9 + (c-1) * 3 + v
        id_1_1_1 = self.kb_3x3.get_var_id(1, 1, 1)
        id_1_1_2 = self.kb_3x3.get_var_id(1, 1, 2)
        id_1_2_1 = self.kb_3x3.get_var_id(1, 2, 1)
        id_2_1_1 = self.kb_3x3.get_var_id(2, 1, 1)
        
        # All should be unique
        ids = [id_1_1_1, id_1_1_2, id_1_2_1, id_2_1_1]
        self.assertEqual(len(ids), len(set(ids)))
    
    def test_get_var_id_formula_correctness(self):
        """Test that ID generation follows the correct formula."""
        # For 3x3: ID = (r-1) * N² + (c-1) * N + v
        # ID(1,1,1) = 0 * 9 + 0 * 3 + 1 = 1
        id_1_1_1 = self.kb_3x3.get_var_id(1, 1, 1)
        self.assertEqual(id_1_1_1, 1)
        
        # ID(1,1,2) = 0 * 9 + 0 * 3 + 2 = 2
        id_1_1_2 = self.kb_3x3.get_var_id(1, 1, 2)
        self.assertEqual(id_1_1_2, 2)
        
        # ID(1,2,1) = 0 * 9 + 1 * 3 + 1 = 4
        id_1_2_1 = self.kb_3x3.get_var_id(1, 2, 1)
        self.assertEqual(id_1_2_1, 4)
        
        # ID(2,1,1) = 1 * 9 + 0 * 3 + 1 = 10
        id_2_1_1 = self.kb_3x3.get_var_id(2, 1, 1)
        self.assertEqual(id_2_1_1, 10)
    
    def test_get_var_id_boundary_values(self):
        """Test ID generation at boundary coordinates."""
        # Top-left corner
        id_1_1_1 = self.kb_3x3.get_var_id(1, 1, 1)
        self.assertIsInstance(id_1_1_1, int)
        self.assertGreater(id_1_1_1, 0)
        
        # Bottom-right corner
        id_3_3_3 = self.kb_3x3.get_var_id(3, 3, 3)
        self.assertIsInstance(id_3_3_3, int)
        self.assertGreater(id_3_3_3, id_1_1_1)
    
    def test_get_var_id_invalid_row(self):
        """Test ID generation fails with invalid row."""
        with self.assertRaises(ValueError):
            self.kb_3x3.get_var_id(0, 1, 1)  # row 0 (should be 1-3)
        
        with self.assertRaises(ValueError):
            self.kb_3x3.get_var_id(4, 1, 1)  # row 4 (should be 1-3)
    
    def test_get_var_id_invalid_col(self):
        """Test ID generation fails with invalid column."""
        with self.assertRaises(ValueError):
            self.kb_3x3.get_var_id(1, 0, 1)  # col 0 (should be 1-3)
        
        with self.assertRaises(ValueError):
            self.kb_3x3.get_var_id(1, 4, 1)  # col 4 (should be 1-3)
    
    def test_get_var_id_invalid_value(self):
        """Test ID generation fails with invalid value."""
        with self.assertRaises(ValueError):
            self.kb_3x3.get_var_id(1, 1, 0)  # value 0 (should be 1-3)
        
        with self.assertRaises(ValueError):
            self.kb_3x3.get_var_id(1, 1, 4)  # value 4 (should be 1-3)
    
    def test_add_clause_single(self):
        """Test adding a single clause."""
        clause = [1, 2, 3]
        self.kb_3x3.add_clause(clause)
        
        self.assertEqual(len(self.kb_3x3), 1)
    
    def test_add_clause_multiple(self):
        """Test adding multiple clauses."""
        clauses = [[1, 2], [3, 4], [5, -6]]
        for clause in clauses:
            self.kb_3x3.add_clause(clause)
        
        self.assertEqual(len(self.kb_3x3), 3)
    
    def test_add_clause_with_negation(self):
        """Test adding clauses with negative literals."""
        clause_with_negation = [1, -2, 3, -4]
        self.kb_3x3.add_clause(clause_with_negation)
        
        self.assertEqual(len(self.kb_3x3), 1)
    
    def test_add_duplicate_clause(self):
        """Test that duplicate clauses are not added twice."""
        clause = [1, 2, 3]
        self.kb_3x3.add_clause(clause)
        self.kb_3x3.add_clause(clause)
        
        # Set should prevent duplicates
        self.assertEqual(len(self.kb_3x3), 1)
    
    def test_add_clause_empty(self):
        """Test adding an empty clause (unsatisfiable)."""
        self.kb_3x3.add_clause([])
        
        self.assertEqual(len(self.kb_3x3), 1)
    
    def test_kb_repr(self):
        """Test knowledge base string representation."""
        self.kb_3x3.add_clause([1, 2])
        self.kb_3x3.add_clause([3, 4])
        repr_str = repr(self.kb_3x3)
        
        self.assertIn("KnowledgeBase", repr_str)
        self.assertIn("3", repr_str)
        self.assertIn("2", repr_str)  # 2 clauses
    
    def test_kb_len(self):
        """Test knowledge base length method."""
        self.assertEqual(len(self.kb_3x3), 0)
        
        self.kb_3x3.add_clause([1, 2])
        self.assertEqual(len(self.kb_3x3), 1)
        
        self.kb_3x3.add_clause([3, 4])
        self.assertEqual(len(self.kb_3x3), 2)


class TestState(unittest.TestCase):
    """Test cases for State class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.board_empty_3x3 = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
        self.board_partial_3x3 = ((1, 0, 0), (0, 2, 0), (0, 0, 3))
        self.board_complete_3x3 = ((1, 2, 3), (2, 3, 1), (3, 1, 2))
    
    def test_state_initialization(self):
        """Test state initialization."""
        state = State(self.board_empty_3x3, None)
        
        self.assertEqual(state.size, 3)
        self.assertEqual(state.board, self.board_empty_3x3)
    
    def test_state_initialization_single_cell(self):
        """Test state initialization with 1x1 board."""
        board_1x1 = ((1,),)
        state = State(board_1x1, None)
        
        self.assertEqual(state.size, 1)
    
    def test_state_initialization_invalid_empty_tuple(self):
        """Test state fails with empty tuple."""
        with self.assertRaises(ValueError):
            State((), None)
    
    def test_state_initialization_invalid_not_tuple(self):
        """Test state fails when not a tuple."""
        with self.assertRaises(ValueError):
            State([[0, 0], [0, 0]], None)
    
    def test_state_hash(self):
        """Test state hashing for set/dict operations."""
        state1 = State(self.board_empty_3x3, None)
        state2 = State(self.board_empty_3x3, None)
        state3 = State(self.board_partial_3x3, None)
        
        # Same board should have same hash
        self.assertEqual(hash(state1), hash(state2))
        
        # Different boards should (likely) have different hash
        self.assertNotEqual(hash(state1), hash(state3))
    
    def test_state_equality(self):
        """Test state equality comparison."""
        state1 = State(self.board_empty_3x3, None)
        state2 = State(self.board_empty_3x3, None)
        state3 = State(self.board_partial_3x3, None)
        
        self.assertEqual(state1, state2)
        self.assertNotEqual(state1, state3)
    
    def test_state_equality_with_different_puzzle_ref(self):
        """Test equality ignores puzzle reference."""
        state1 = State(self.board_empty_3x3, "puzzle1")
        state2 = State(self.board_empty_3x3, "puzzle2")
        
        self.assertEqual(state1, state2)  # Should be equal based on board only
    
    def test_state_inequality_with_non_state(self):
        """Test inequality with non-State objects."""
        state = State(self.board_empty_3x3, None)
        
        self.assertNotEqual(state, "not a state")
        self.assertNotEqual(state, self.board_empty_3x3)
        self.assertNotEqual(state, None)
    
    def test_state_in_set(self):
        """Test states can be used in sets."""
        state1 = State(self.board_empty_3x3, None)
        state2 = State(self.board_empty_3x3, None)  # Identical
        state3 = State(self.board_partial_3x3, None)
        
        state_set = {state1, state2, state3}
        
        # state1 and state2 are equal, so set should have 2 elements
        self.assertEqual(len(state_set), 2)
    
    def test_state_repr(self):
        """Test state string representation."""
        state = State(self.board_empty_3x3, None)
        repr_str = repr(state)
        
        self.assertIn("State", repr_str)
        self.assertIn("3x3", repr_str)
    
    def test_state_str_empty_board(self):
        """Test state detailed string representation with empty board."""
        state = State(self.board_empty_3x3, None)
        str_repr = str(state)
        
        # Should show dots for empty cells
        self.assertIn(".", str_repr)
        self.assertEqual(str_repr.count("."), 9)
    
    def test_state_str_partial_board(self):
        """Test state detailed string representation with partial board."""
        state = State(self.board_partial_3x3, None)
        str_repr = str(state)
        
        # Should show numbers and dots
        self.assertIn("1", str_repr)
        self.assertIn("2", str_repr)
        self.assertIn("3", str_repr)
        self.assertIn(".", str_repr)
    
    def test_state_str_complete_board(self):
        """Test state detailed string representation with complete board."""
        state = State(self.board_complete_3x3, None)
        str_repr = str(state)
        
        # Should contain all values, no dots
        self.assertNotIn(".", str_repr)
        self.assertIn("1", str_repr)
        self.assertIn("2", str_repr)
        self.assertIn("3", str_repr)
    
    def test_is_complete_empty_board(self):
        """Test is_complete returns False for empty board."""
        state = State(self.board_empty_3x3, None)
        
        self.assertFalse(state.is_complete())
    
    def test_is_complete_partial_board(self):
        """Test is_complete returns False for partially filled board."""
        state = State(self.board_partial_3x3, None)
        
        self.assertFalse(state.is_complete())
    
    def test_is_complete_full_board(self):
        """Test is_complete returns True for completely filled board."""
        state = State(self.board_complete_3x3, None)
        
        self.assertTrue(state.is_complete())
    
    def test_is_complete_single_cell_empty(self):
        """Test is_complete on 1x1 empty board."""
        state = State(((0,),), None)
        
        self.assertFalse(state.is_complete())
    
    def test_is_complete_single_cell_filled(self):
        """Test is_complete on 1x1 filled board."""
        state = State(((1,),), None)
        
        self.assertTrue(state.is_complete())
    
    def test_state_immutability(self):
        """Test that state board is immutable."""
        state = State(self.board_empty_3x3, None)
        
        # Trying to modify should raise TypeError
        with self.assertRaises(TypeError):
            state.board[0][0] = 1


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components."""
    
    def test_board_with_state_and_kb(self):
        """Test creating a complete puzzle setup."""
        # Create initial state
        initial_board = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
        state = State(initial_board, None)
        
        # Create board
        constraints = ((0, 0, '<'), (1, 1, '>'))
        board = Board(3, state, constraints)
        
        # Create knowledge base
        kb = KnowledgeBase(3)
        kb.add_clause([1, 2, 3])  # (pos[0,0]=1) OR (pos[0,0]=2) OR (pos[0,0]=3)
        
        # Verify integration
        self.assertEqual(board.N, 3)
        self.assertEqual(state.size, 3)
        self.assertEqual(len(kb), 1)
    
    def test_multiple_states_with_same_kb(self):
        """Test using same KB with different states."""
        kb = KnowledgeBase(4)
        
        # Add some clauses
        for i in range(1, 5):
            kb.add_clause([i, i+4, i+8])
        
        # Create multiple states
        state1 = State(tuple(tuple(0 for _ in range(4)) for _ in range(4)), None)
        state2 = State(tuple(tuple(1 for _ in range(4)) for _ in range(4)), None)
        
        # Both states should work with same KB
        self.assertEqual(len(kb), 4)
        self.assertFalse(state1.is_complete())
        self.assertTrue(state2.is_complete())


if __name__ == '__main__':
    unittest.main(verbosity=2)
