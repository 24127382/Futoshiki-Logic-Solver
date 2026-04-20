"""
SOLVER INTEGRATION GUIDE
========================
This file shows what the Solver classes MUST implement to work with the GUI.

Location: Add this to each solver file or create a base class in src/solvers/base.py
"""

from typing import List, Tuple, Dict, Any
from gui.bridge import InputData, OutputData
import time


# ============================================================================
# INTERFACE: What Solvers Must Implement
# ============================================================================

class SolverInterface:
    """
    Base class / Interface for all solvers.
    
    Each solver (Backtracking, ForwardChaining, AStar) must implement this.
    """
    
    def __init__(self, timeout: float = 30.0):
        """
        Initialize solver.
        
        Args:
            timeout: Max seconds to spend solving
        """
        self.timeout = timeout
        self.start_time = None
        self.elapsed_time = 0.0
        self.iterations = 0
    
    def solve(self, input_data: InputData) -> OutputData:
        """
        Solve the puzzle.
        
        MUST BE IMPLEMENTED BY SUBCLASSES.
        
        Args:
            input_data: InputData with size, matrix, constraints
        
        Returns:
            OutputData with status, solution, stats
        """
        raise NotImplementedError("Subclasses must implement solve()")
    
    def _check_timeout(self) -> bool:
        """
        Check if timeout exceeded.
        
        Returns:
            True if should stop solving
        """
        if self.start_time is None:
            self.start_time = time.time()
            return False
        
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout:
            self.elapsed_time = elapsed
            return True
        
        return False
    
    def _create_success_output(self, solution: List[List[int]]) -> OutputData:
        """Helper to create success OutputData."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        return OutputData(
            status='success',
            solution=solution,
            stats={
                'time_ms': elapsed * 1000,
                'iterations': self.iterations,
                'solver': self.__class__.__name__
            },
            message='Puzzle solved successfully'
        )
    
    def _create_failure_output(self, reason: str = 'unsolvable') -> OutputData:
        """Helper to create failure OutputData."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        return OutputData(
            status=reason,  # 'unsolvable', 'timeout', 'error'
            solution=None,
            stats={
                'time_ms': elapsed * 1000,
                'iterations': self.iterations,
                'solver': self.__class__.__name__
            },
            message=f'Puzzle {reason}'
        )


# ============================================================================
# EXAMPLE: Backtracking Solver (Adapted)
# ============================================================================

class BacktrackingSolverExample:
    """
    Example of how to adapt BacktrackingSolver to the new interface.
    
    Copy this pattern to src/solvers/backtracking.py
    """
    
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.start_time = None
        self.iterations = 0
    
    def solve(self, input_data: InputData) -> OutputData:
        """
        Solve via backtracking.
        
        Args:
            input_data: InputData from GUI
        
        Returns:
            OutputData with solution
        """
        self.start_time = time.time()
        self.iterations = 0
        
        try:
            # Extract data
            size = input_data.size
            matrix = [row[:] for row in input_data.matrix]  # Copy
            constraints = input_data.constraints
            
            # Run backtracking
            if self._backtrack(matrix, size, constraints):
                return OutputData(
                    status='success',
                    solution=matrix,
                    stats={
                        'time_ms': (time.time() - self.start_time) * 1000,
                        'iterations': self.iterations,
                        'solver': 'Backtracking'
                    },
                    message='Puzzle solved successfully'
                )
            else:
                return OutputData(
                    status='unsolvable',
                    solution=None,
                    stats={
                        'time_ms': (time.time() - self.start_time) * 1000,
                        'iterations': self.iterations,
                        'solver': 'Backtracking'
                    },
                    message='Puzzle is unsolvable'
                )
        
        except Exception as e:
            return OutputData(
                status='error',
                solution=None,
                stats={
                    'time_ms': (time.time() - self.start_time) * 1000,
                    'iterations': self.iterations,
                    'solver': 'Backtracking'
                },
                message=f'Error: {str(e)}'
            )
    
    def _backtrack(self, matrix: List[List[int]], size: int, 
                   constraints: List[Tuple]) -> bool:
        """
        Your existing backtracking logic here.
        
        Insert your current implementation.
        """
        # TODO: Paste your existing backtracking algorithm
        
        # Example skeleton:
        # for r in range(size):
        #     for c in range(size):
        #         if matrix[r][c] == 0:
        #             for num in range(1, size + 1):
        #                 if self._is_valid(matrix, r, c, num, constraints):
        #                     matrix[r][c] = num
        #                     self.iterations += 1
        #                     
        #                     if self._check_timeout():
        #                         return False
        #                     
        #                     if self._backtrack(matrix, size, constraints):
        #                         return True
        #                     
        #                     matrix[r][c] = 0
        #             return False
        # return True
        
        pass


# ============================================================================
# CONVERTING EXISTING SOLVERS
# ============================================================================

"""
MIGRATION CHECKLIST for each solver:

1. Update solve() signature:
   FROM: def solve(board: Board) -> List[List[int]]
   TO:   def solve(input_data: InputData) -> OutputData

2. Extract data from InputData:
   matrix = input_data.matrix
   constraints = input_data.constraints
   size = input_data.size

3. Use _check_timeout() in your loops:
   if self._check_timeout():
       return self._create_failure_output('timeout')

4. Track iterations:
   self.iterations += 1  # In your main search loop

5. Return OutputData instead of just the matrix:
   return self._create_success_output(solved_matrix)
   return self._create_failure_output('unsolvable')

6. Wrap in try/except:
   return self._create_failure_output('error')

7. Test:
   input_data = InputData(size=4, matrix=[...], constraints=[...])
   output = solver.solve(input_data)
   assert output.status in ['success', 'unsolvable', 'timeout']
"""


# ============================================================================
# TESTING THE SOLVER INTEGRATION
# ============================================================================

def test_solver_integration():
    """
    Example test to verify solver integration.
    
    Run this to make sure your solver works with the GUI.
    """
    # Create test input
    test_input = InputData(
        size=4,
        matrix=[
            [0, 0, 0, 1],
            [0, 2, 0, 0],
            [0, 0, 0, 0],
            [4, 0, 0, 0]
        ],
        constraints=[
            ((0, 0), (0, 1), '<'),
            ((0, 1), (1, 1), '>'),
        ]
    )
    
    # Create solver instance
    # solver = BacktrackingSolverExample(timeout=30)
    # output = solver.solve(test_input)
    
    # Verify output structure
    # assert isinstance(output, OutputData)
    # assert output.status in ['success', 'unsolvable', 'timeout', 'error']
    # if output.status == 'success':
    #     assert output.solution is not None
    #     assert len(output.solution) == 4
    #     assert output.stats['time_ms'] > 0
    # 
    # print(f"✓ Solver test passed: {output.status}")
    # print(f"  Time: {output.stats['time_ms']:.2f}ms")
    # print(f"  Iterations: {output.stats['iterations']}")
    
    pass


if __name__ == "__main__":
    test_solver_integration()
