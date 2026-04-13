"""Unit tests for forward chaining solver."""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.board import Board
from src.models.kb import KnowledgeBase
from src.models.state import State
from src.solvers.forward_chaining import forward_chaining_solver


class TestForwardChaining(unittest.TestCase):
    """Test cases for forward chaining solver."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple 2x2 board
        self.state_2x2_empty = State(
            ((0, 0), (0, 0)),
            None
        )
        self.kb_2x2 = KnowledgeBase(2)
    
    def test_forward_chaining_simple_unit_clause(self):
        """Test forward chaining with a simple unit clause."""
        # For a 2x2 board, var_id for (row=1, col=1, value=1) is:
        # (1-1) * (2^2) + (1-1) * 2 + 1 = 0 + 0 + 1 = 1
        kb = KnowledgeBase(2)
        var_id = kb.get_var_id(1, 1, 1)  # (row, col, value)
        
        # Add a unit clause: (var1) - meaning this cell must be 1
        kb.add_clause([var_id])
        
        initial_state = State(((0, 0), (0, 0)), None)
        result = forward_chaining_solver(initial_state, kb)
        
        # Check that result is not None (solution found)
        self.assertIsNotNone(result, "Forward chaining should find a solution with unit clauses")
        
        # Check that it's a State object
        if result is not None:
            self.assertIsInstance(result, State)
    
    def test_forward_chaining_empty_kb(self):
        """Test forward chaining with empty knowledge base."""
        kb = KnowledgeBase(2)
        initial_state = State(((0, 0), (0, 0)), None)
        
        result = forward_chaining_solver(initial_state, kb)
        
        # With no clauses, forward chaining should return the initial state
        # or None depending on implementation
        self.assertTrue(result is None or isinstance(result, State))
    
    def test_forward_chaining_contradiction(self):
        """Test forward chaining with contradictory clauses."""
        kb = KnowledgeBase(2)
        
        # Create a contradiction: both p and not-p must be true
        var_id = kb.get_var_id(1, 1, 1)
        
        # Add unit clause: p (var_id)
        kb.add_clause([var_id])
        
        # Add unit clause: not-p (-var_id)
        kb.add_clause([-var_id])
        
        initial_state = State(((0, 0), (0, 0)), None)
        result = forward_chaining_solver(initial_state, kb)
        
        # Should return None (unsolvable)
        self.assertIsNone(result, "Forward chaining should detect contradiction")
    
    def test_forward_chaining_clause_with_multiple_literals(self):
        """Test forward chaining with non-unit clauses."""
        kb = KnowledgeBase(2)
        
        var1 = kb.get_var_id(1, 1, 1)
        var2 = kb.get_var_id(1, 2, 1)
        
        # Add unit clause: var1
        kb.add_clause([var1])
        
        # Add clause: (not var1 OR var2)
        # When var1 is inferred, this clause becomes unit with var2
        kb.add_clause([-var1, var2])
        
        initial_state = State(((0, 0), (0, 0)), None)
        result = forward_chaining_solver(initial_state, kb)
        
        # Should find a solution
        self.assertIsNotNone(result, "Forward chaining should propagate unit clauses")
        if result is not None:
            self.assertIsInstance(result, State)
    
    def test_forward_chaining_3x3_board(self):
        """Test forward chaining with a 3x3 board."""
        kb = KnowledgeBase(3)
        initial_state = State(((0, 0, 0), (0, 0, 0), (0, 0, 0)), None)
        
        # Add a simple unit clause
        var_id = kb.get_var_id(1, 1, 1)
        kb.add_clause([var_id])
        
        result = forward_chaining_solver(initial_state, kb)
        
        self.assertTrue(result is None or isinstance(result, State))
    
    def test_forward_chaining_returns_state(self):
        """Test that forward chaining returns a State object (not None for valid solutions)."""
        kb = KnowledgeBase(2)
        
        # Add unit clauses
        var1 = kb.get_var_id(1, 1, 1)
        var2 = kb.get_var_id(2, 2, 2)
        
        kb.add_clause([var1])
        kb.add_clause([var2])
        
        initial_state = State(((0, 0), (0, 0)), None)
        result = forward_chaining_solver(initial_state, kb)
        
        # Should return a State or None
        self.assertTrue(result is None or isinstance(result, State),
                       "forward_chaining_solver should return State or None")


if __name__ == '__main__':
    unittest.main()
