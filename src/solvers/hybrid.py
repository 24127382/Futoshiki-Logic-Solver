import time
import threading
from typing import List, Tuple, Set, Dict, Optional
from collections import deque

from src.models.state import State
from src.models.board import Board
from src.logic.grounding import ground_axioms
from src.models.kb import KnowledgeBase
from gui.bridge import InputData, OutputData
from src.solvers.backtracking import BacktrackingSolver
from src.solvers.forward_chaining import ForwardChainingSolver

class AC3Solver:
    """
    Arc Consistency (AC-3) solver for Futoshiki.
    Prunes domains based on constraints.
    """
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.start_time = 0.0

    def solve(self, input_data: InputData, stop_event: threading.Event = None) -> OutputData:
        self.start_time = time.time()
        N = input_data.size
        
        # Initialize domains
        domains = {}
        for r in range(N):
            for c in range(N):
                val = input_data.matrix[r][c]
                if val != 0:
                    domains[(r, c)] = {val}
                else:
                    domains[(r, c)] = set(range(1, N + 1))

        # Constraints (arcs)
        arcs = deque()
        # Row constraints
        for r in range(N):
            for c1 in range(N):
                for c2 in range(N):
                    if c1 != c2:
                        arcs.append(((r, c1), (r, c2), "diff"))
        # Col constraints
        for c in range(N):
            for r1 in range(N):
                for r2 in range(N):
                    if r1 != r2:
                        arcs.append(((r1, c), (r2, c), "diff"))
        # Inequality constraints
        for (r1, c1), (r2, c2), op in input_data.constraints:
            arcs.append(((r1, c1), (r2, c2), op))
            # Also add the reverse arc
            rev_op = ">" if op == "<" else "<"
            arcs.append(((r2, c2), (r1, c1), rev_op))

        # AC-3 Algorithm
        while arcs:
            if stop_event and stop_event.is_set():
                return OutputData(status='timeout', stats={'time_ms': (time.time() - self.start_time)*1000})
            
            (xi, xj), op = arcs.popleft()
            if self._revise(domains, xi, xj, op):
                if not domains[xi]:
                    return OutputData(status='unsolvable', stats={'time_ms': (time.time() - self.start_time)*1000})
                
                # Add neighbors of xi back to queue
                for neighbor in self._get_neighbors(xi, xj, N, input_data.constraints):
                    arcs.append((neighbor, xi, self._get_op(neighbor, xi, input_data.constraints)))

        # Convert domains back to solution
        solution = [[0]*N for _ in range(N)]
        is_complete = True
        for (r, c), d in domains.items():
            if len(d) == 1:
                solution[r][c] = list(d)[0]
            else:
                solution[r][c] = 0
                is_complete = False

        status = 'success' if is_complete else 'incomplete'
        return OutputData(
            status=status,
            solution=solution if is_complete else solution,
            stats={'time_ms': round((time.time() - self.start_time)*1000, 2), 'algorithm': 'AC-3'},
            message="AC-3 completed"
        )

    def _revise(self, domains, xi, xj, op) -> bool:
        revised = False
        to_remove = set()
        for x in domains[xi]:
            # Check if there is any y in domains[xj] that satisfies the constraint
            satisfied = False
            for y in domains[xj]:
                if op == "diff":
                    if x != y:
                        satisfied = True
                        break
                elif op == "<":
                    if x < y:
                        satisfied = True
                        break
                elif op == ">":
                    if x > y:
                        satisfied = True
                        break
            if not satisfied:
                to_remove.add(x)
                revised = True
        
        for x in to_remove:
            domains[xi].remove(x)
        return revised

    def _get_neighbors(self, xi, xj, N, constraints):
        neighbors = []
        r, c = xi
        # Same row
        for i in range(N):
            if i != c and (r, i) != xj:
                neighbors.append((r, i))
        # Same col
        for i in range(N):
            if i != r and (i, c) != xj:
                neighbors.append((i, c))
        # Inequalities
        for (r1, c1), (r2, c2), op in constraints:
            if (r1, c1) == xi and (r2, c2) != xj:
                neighbors.append((r2, c2))
            if (r2, c2) == xi and (r1, c1) != xj:
                neighbors.append((r1, c1))
        return list(set(neighbors))

    def _get_op(self, xi, xj, constraints):
        # Determine the operator between xi and xj
        if xi[0] == xj[0] or xi[1] == xj[1]:
            return "diff"
        for (r1, c1), (r2, c2), op in constraints:
            if (r1, c1) == xi and (r2, c2) == xj: return op
            if (r1, c1) == xj and (r2, c2) == xi: return ">" if op == "<" else "<"
        return "diff"

class HybridSolver:
    """
    Hybrid solvers combining FC and Backtracking.
    """
    def __init__(self, mode: str = "pure", timeout: float = 30.0):
        self.mode = mode # "pure" or "hybrid" (AC-3)
        self.timeout = timeout

    def solve(self, input_data: InputData, stop_event: threading.Event = None) -> OutputData:
        start_time = time.time()
        
        # 1. Run inference (FC or AC-3)
        if self.mode == "pure":
            fc_solver = ForwardChainingSolver(timeout=self.timeout)
            inference_output = fc_solver.solve(input_data, stop_event)
        else:
            ac3_solver = AC3Solver(timeout=self.timeout)
            inference_output = ac3_solver.solve(input_data, stop_event)

        if stop_event and stop_event.is_set():
            return inference_output

        if inference_output.status == 'success':
            inference_output.stats['algorithm'] = f"FC-{self.mode} + Fallback (Solved by inference)"
            return inference_output
        
        if inference_output.status == 'unsolvable' and self.mode == "pure":
             # FC-pure returns unsolvable if it finds a contradiction
             return inference_output

        # 2. If incomplete, run Backtracking on partial solution
        partial_matrix = inference_output.solution
        if not partial_matrix:
            partial_matrix = input_data.matrix # Fallback to original if inference failed

        fallback_input = InputData(
            size=input_data.size,
            matrix=partial_matrix,
            constraints=input_data.constraints
        )
        
        bt_solver = BacktrackingSolver(timeout=self.timeout - (time.time() - start_time))
        bt_output = bt_solver.solve(fallback_input, stop_event)
        
        total_time_ms = (time.time() - start_time) * 1000
        bt_output.stats['time_ms'] = round(total_time_ms, 2)
        bt_output.stats['algorithm'] = f"FC-{self.mode} + Fallback Backtracking"
        
        return bt_output

class BruteforceSolver(BacktrackingSolver):
    """
    Simplified backtracking that behaves more like a brute force.
    (Actually the current BacktrackingSolver is already simple).
    """
    def solve(self, input_data: InputData, stop_event: threading.Event = None) -> OutputData:
        output = super().solve(input_data, stop_event)
        output.stats['algorithm'] = 'Bruteforce'
        return output
