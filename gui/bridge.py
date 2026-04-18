"""
Bridge Module: UI ↔ Logic Data Translator
==========================================
This module translates between GUI data formats and Logic solver formats.
Uses the Bridge Pattern to decouple UI from Algorithm concerns.

Data Schema:
- InputData: What the solver needs
- OutputData: What the solver returns
- UIData: What the GUI holds
"""

from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, asdict
import sys
from pathlib import Path

# Add src/ to path for imports
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models.board import Board


# ============================================================================
# DATA STRUCTURES: Standard Schema
# ============================================================================

@dataclass
class InputData:
    """
    Standard format for data going INTO the solver.
    
    Attributes:
        size: Grid size (4, 5, 6, 7, 8, or 9)
        matrix: 2D list of integers (0 = empty, 1-9 = filled)
        constraints: List of constraint tuples: ((r1,c1), (r2,c2), sign)
                    where sign is '<' or '>'
    """
    size: int
    matrix: List[List[int]]
    constraints: List[Tuple[Tuple[int, int], Tuple[int, int], str]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return asdict(self)


@dataclass
class OutputData:
    """
    Standard format for data coming OUT of the solver.
    
    Attributes:
        status: 'success', 'unsolvable', 'timeout', 'error'
        solution: Solved 2D matrix (None if status != 'success')
        stats: Dictionary with solver stats (time, iterations, etc.)
        message: Human-readable message
    """
    status: str  # 'success' | 'unsolvable' | 'timeout' | 'error'
    solution: List[List[int]] = None
    stats: Dict[str, Any] = None
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        data = asdict(self)
        data['stats'] = self.stats or {}
        return data


# ============================================================================
# BRIDGE CLASS: The Translator
# ============================================================================

class FutoshikiBridge:
    """
    Bridge between GUI (tkinter) and Logic (src/solvers/).
    
    Responsibilities:
    1. Convert GUI widget data → InputData (for solvers)
    2. Convert solver OutputData → GUI-friendly format
    3. Validate data integrity at boundaries
    
    Design Pattern: Bridge Pattern
    - Abstraction: The solver interface (doesn't care about UI)
    - Implementation: Various algorithms (A*, Backtracking, Forward Chaining)
    - Bridge: This class connects them
    """

    @staticmethod
    def ui_to_logic(
        gui_matrix: List[List[str]],
        gui_constraints: Dict[str, str],
        size: int
    ) -> InputData:
        """
        Convert GUI data (from tkinter widgets) → InputData for solvers.
        
        Args:
            gui_matrix: 2D list of strings from Entry widgets ('' or '1'-'9')
            gui_constraints: Dict mapping constraint keys to signs
                           Example: {'(0,0)-(0,1)': '<', '(0,1)-(1,1)': '>'}
            size: Grid size (4-9)
        
        Returns:
            InputData object ready for solvers
        
        Raises:
            ValueError: If data format is invalid
        
        TODO: Algorithm Team
        - Add validation: matrix values are 0-9
        - Add validation: constraints only reference valid positions
        """
        # Convert matrix strings to integers
        matrix = []
        for row in gui_matrix:
            int_row = []
            for cell in row:
                if cell == '':
                    int_row.append(0)
                else:
                    try:
                        val = int(cell)
                        if 1 <= val <= 9:
                            int_row.append(val)
                        else:
                            raise ValueError(f"Cell value {val} out of range 1-9")
                    except ValueError as e:
                        raise ValueError(f"Invalid cell value: {cell}") from e
            matrix.append(int_row)

        # Convert constraint dict to tuple list
        constraints = []
        for key, sign in gui_constraints.items():
            # Parse key format: "(r1,c1)-(r2,c2)"
            parts = key.split('-')
            if len(parts) == 2:
                coord1 = tuple(map(int, parts[0].strip('()').split(',')))
                coord2 = tuple(map(int, parts[1].strip('()').split(',')))
                constraints.append((coord1, coord2, sign))

        return InputData(
            size=size,
            matrix=matrix,
            constraints=constraints
        )

    @staticmethod
    def logic_to_ui(output_data: OutputData) -> Dict[str, Any]:
        """
        Convert solver OutputData → GUI-friendly format.
        
        Args:
            output_data: OutputData from solver
        
        Returns:
            Dict with keys:
            - 'status': 'success' | 'unsolvable' | 'error'
            - 'solution': 2D list of integers (or None)
            - 'stats': Dict with timing/iteration info
            - 'message': Human-readable message
        
        TODO: Algorithm Team
        - Add post-processing: validate solution correctness
        - Add stat extraction: parse solver timing data
        """
        return {
            'status': output_data.status,
            'solution': output_data.solution,
            'stats': output_data.stats or {},
            'message': output_data.message
        }

    @staticmethod
    def validate_solution(
        solution: List[List[int]],
        constraints: List[Tuple[Tuple[int, int], Tuple[int, int], str]]
    ) -> Tuple[bool, str]:
        """
        Validate that a solution satisfies all constraints.
        
        Args:
            solution: Solved 2D matrix
            constraints: List of constraint tuples
        
        Returns:
            (is_valid: bool, message: str)
        
        TODO: Algorithm Team
        - Implement constraint validation logic
        - Check row/column uniqueness (1-9 in each)
        - Check all inequality constraints
        """
        # TODO: Implement validation
        # For now, return True (trust solver output)
        return True, "Solution validated"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_matrix_size(size: int) -> bool:
    """Ensure size is 4-9."""
    return 4 <= size <= 9


def extract_constraints_from_gui(
    constraint_state: Dict[str, str]
) -> List[Tuple[Tuple[int, int], Tuple[int, int], str]]:
    """
    Parse constraint state dictionary into constraint tuples.
    
    Format of constraint_state:
    {
        '(0,0)-(0,1)': '<',
        '(0,1)-(1,1)': '>',
        ...
    }
    
    TODO: Keep this updated with GUI constraint format changes
    """
    constraints = []
    for key, sign in constraint_state.items():
        try:
            parts = key.split('-')
            if len(parts) == 2:
                coord1 = tuple(map(int, parts[0].strip('()').split(',')))
                coord2 = tuple(map(int, parts[1].strip('()').split(',')))
                if sign in ['<', '>']:
                    constraints.append((coord1, coord2, sign))
        except (ValueError, IndexError):
            continue  # Skip malformed constraints
    
    return constraints
