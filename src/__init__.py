"""Futoshiki Solver Package"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Package-level imports
from src.models.board import Board
from src.models.state import State
from src.models.kb import KnowledgeBase

__all__ = [
    "Board",
    "State", 
    "KnowledgeBase",
]
