# Futoshiki Solver

A comprehensive solver for Futoshiki puzzles using multiple AI algorithms and approaches.

## Overview

Futoshiki (不等式, meaning "inequality") is a logic puzzle similar to Sudoku. The goal is to fill a grid with numbers such that:
- Each row contains unique numbers from 1 to N
- Each column contains unique numbers from 1 to N  
- All inequality constraints are satisfied

This project implements multiple solving strategies to compare their efficiency:

## Features

- **Multiple Solver Algorithms**
  - A* Search with heuristics
  - Backtracking
  - Forward Chaining (logic programming)
  - Backward Chaining (logic programming)

- **Knowledge Base & Logic**
  - Axioms and constraint definitions
  - CNF converter for logical formulas
  - Grounding for proposition instantiation

- **Utilities**
  - Puzzle parser for input files
  - Heuristic functions for informed search
  - GUI for interactive puzzle solving (optional)

## Project Structure

```
futoshiki-solver/
├── src/
│   ├── logic/              # Logical reasoning & constraint handling
│   │   ├── axioms.py
│   │   ├── cnf_converter.py
│   │   └── grounding.py
│   ├── models/             # Data structures
│   │   ├── board.py        # Puzzle board representation
│   │   ├── kb.py           # Knowledge base
│   │   └── state.py        # Search state
│   ├── solvers/            # Algorithm implementations
│   │   ├── a_star.py
│   │   ├── backtracking.py
│   │   ├── forward_chaining.py
│   │   └── backward_chaining.py
│   └── utils/              # Helper functions
│       ├── heuristic.py
│       └── parser.py
├── tests/                  # Unit tests
├── inputs/                 # Sample puzzle inputs
├── outputs/                # Solution outputs
├── experiments/            # Experiment scripts & analysis
├── gui/                    # GUI components (optional)
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
└── pyproject.toml          # Project configuration
```

## Installation

### Prerequisites
- Python 3.8+

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/futoshiki-solver.git
cd futoshiki-solver
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

## Usage

### Basic Solving
```bash
python main.py --input inputs/puzzle.txt --solver a_star
```

### Options
- `--solver`: Choose solver algorithm (a_star, backtracking, forward_chaining, backward_chaining)
- `--input`: Path to input puzzle file
- `--output`: Path to save solution (default: outputs/)
- `--verbose`: Enable detailed logging

### Input Format
Puzzle files should follow the standard Futoshiki format with numbers and inequality symbols.

## Testing

Run the test suite:
```bash
pytest
pytest --cov  # With coverage report
```

## Performance Comparison

See `experiments/` for benchmarking scripts comparing algorithm performance.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Author

Your Name (your.email@example.com)
