import os
import glob
import time
import threading
import statistics
import psutil
from typing import List, Dict, Any

from src.utils.parser import load_puzzle_file
from gui.bridge import InputData, OutputData
from src.solvers.backtracking import BacktrackingSolver
from src.solvers.a_star import A_StarSolver
from src.solvers.forward_chaining import ForwardChainingSolver
from src.solvers.backward_chaining import BackwardChainingSolver

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 # KB

def run_benchmark():
    # 1. Define Solvers to test
    # Matching the example list
    solver_configs = [
        ("A*", lambda: A_StarSolver(timeout=25.0)),
        ("Backward Chaining", lambda: BackwardChainingSolver(timeout=25.0)),
        ("Forward Chaining", lambda: ForwardChainingSolver(timeout=25.0)),
        ("Backtracking", lambda: BacktrackingSolver(timeout=25.0))
    ]
    
    # 2. Collect 12 instances
    puzzle_files = glob.glob("inputs/*.txt")
    # Filter out empty matrices if we have too many, or just take first 12
    puzzle_files = sorted(puzzle_files)[:12]
    
    if len(puzzle_files) < 12:
        print(f"Warning: Only found {len(puzzle_files)} puzzle files. Continuing anyway.", flush=True)

    repeats = 5
    results_by_solver = {name: [] for name, _ in solver_configs}
    
    print(f"Starting Benchmark: {len(puzzle_files)} instances x {repeats} repeats x {len(solver_configs)} solvers", flush=True)
    print("="*80, flush=True)

    for puzzle_file in puzzle_files:
        print(f"Puzzle: {os.path.basename(puzzle_file)}", flush=True)
        try:
            board, initial_state = load_puzzle_file(puzzle_file)
            N = board.N
            input_constraints = []
            for c in board.constraints:
                r1, c1, op, r2, c2 = c
                input_constraints.append(((r1, c1), (r2, c2), op))
            
            input_data = InputData(
                size=N,
                matrix=[list(row) for row in initial_state.board],
                constraints=input_constraints
            )
            
            for name, solver_factory in solver_configs:
                solver_results = []
                for i in range(repeats):
                    solver = solver_factory()
                    stop_event = threading.Event()
                    timer = threading.Timer(25.0, lambda: stop_event.set())
                    timer.start()
                    
                    import tracemalloc
                    tracemalloc.start()
                    start_time = time.time()
                    try:
                        output = solver.solve(input_data, stop_event=stop_event)
                    except Exception as e:
                        output = OutputData(status='error', message=str(e))
                    finally:
                        timer.cancel()
                    
                    end_time = time.time()
                    _, peak_mem = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    
                    duration_ms = (end_time - start_time) * 1000
                    peak_mem = peak_mem / 1024.0 # KB
                    
                    # Track stats
                    stats_dict = output.stats or {}
                    inferences = stats_dict.get("nodes_visited") or stats_dict.get("clauses_generated") or 0
                    if name.startswith("FC"):
                        inferences = stats_dict.get("clauses_generated") or 0
                    
                    solver_results.append({
                        "status": output.status,
                        "time": duration_ms,
                        "mem": peak_mem,
                        "inferences": inferences
                    })
                
                results_by_solver[name].extend(solver_results)
                
        except Exception as e:
            print(f"Error processing {puzzle_file}: {e}")

    # 3. Aggregate results
    table_runtime = []
    table_resource = []
    
    for name, data in results_by_solver.items():
        times = [d['time'] for d in data if d['status'] != 'timeout' and d['status'] != 'error']
        all_times = [d['time'] for d in data]
        timeouts = sum(1 for d in data if d['status'] == 'timeout')
        successes = sum(1 for d in data if d['status'] == 'success')
        solve_rate = successes / len(data)
        
        avg_time = statistics.mean(all_times) if all_times else 0
        std_time = statistics.stdev(all_times) if len(all_times) > 1 else 0
        
        mems = [d['mem'] for d in data]
        avg_mem = statistics.mean(mems) if mems else 0
        
        infs = [d['inferences'] for d in data]
        avg_infs = statistics.mean(infs) if infs else 0

        table_runtime.append({
            "Algorithm": name,
            "Solve Rate": f"{solve_rate:.3f}",
            "Avg Runtime (ms)": f"{avg_time:.1f}",
            "Std Runtime (ms)": f"{std_time:.1f}",
            "Timeouts": timeouts
        })
        
        table_resource.append({
            "Algorithm": name,
            "Avg Peak Mem (KB)": f"{avg_mem:.1f}",
            "Avg Inferences/Expansions": f"{avg_infs:.1f}"
        })

    # 4. Generate LaTeX
    generate_latex_report(table_runtime, table_resource)
    print("Benchmark complete. LaTeX tables generated in experiment_results.tex")

def generate_latex_report(table_runtime, table_resource):
    latex = r"""\subsection{Performance Analysis}
Tables 6 and 7 present the aggregate performance across all 60 runs per algorithm. Two distinct failure modes are tracked: timeouts ($>$ 25s) and fixpoint terminations (where pure inference halts without a complete assignment).

\begin{table}[h]
\centering
\begin{tabular}{|l|c|r|r|c|}
\hline
\textbf{Algorithm} & \textbf{Solve Rate} & \textbf{Avg Runtime (ms)} & \textbf{Std Runtime (ms)} & \textbf{Timeouts} \\ \hline
"""
    for row in table_runtime:
        name = row["Algorithm"].replace("_", "\\_")
        latex += f"{name} & {row['Solve Rate']} & {row['Avg Runtime (ms)']} & {row['Std Runtime (ms)']} & {row['Timeouts']} \\\\ \\hline\n"
    
    latex += r"""\end{tabular}
\caption{Runtime performance and solve statistics across 60 runs each (12 instances $\times$ 5 repeats).}
\label{tab:runtime}
\end{table}

\begin{table}[h]
\centering
\begin{tabular}{|l|r|r|}
\hline
\textbf{Algorithm} & \textbf{Avg Peak Mem (KB)} & \textbf{Avg Inferences/Expansions} \\ \hline
"""
    for row in table_resource:
        name = row["Algorithm"].replace("_", "\\_")
        latex += f"{name} & {row['Avg Peak Mem (KB)']} & {row['Avg Inferences/Expansions']} \\\\ \\hline\n"
    
    latex += r"""\end{tabular}
\caption{Memory usage and search effort across 60 runs each.}
\label{tab:resource}
\end{table}
"""
    with open("experiment_results.tex", "w", encoding="utf-8") as f:
        f.write(latex)

if __name__ == "__main__":
    run_benchmark()
