# Futoshiki Solver

A comprehensive solver for Futoshiki puzzles using multiple AI algorithms and approaches.

## Overview

Futoshiki (不等式, meaning "inequality") is a logic puzzle similar to Sudoku. The goal is to fill a grid with numbers such that:
- Each row contains unique numbers from 1 to N
- Each column contains unique numbers from 1 to N  
- All inequality constraints are satisfied

This project implements multiple solving strategies to compare their efficiency:

## Features

✅ **Implemented Features:**

- **Multiple Solver Algorithms**
  - ✅ Backtracking solver with constraint satisfaction
  - ✅ Forward Chaining (logic programming approach)
  - ✅ Backward Chaining (logic programming approach)
  - ✅ A* Search with heuristics

- **Knowledge Base & Logic**
  - ✅ Axioms and constraint definitions (axioms.py)
  - ✅ Grounding for proposition instantiation
  - ✅ Logic utilities for reasoning

- **User Interface**
  - ✅ Modern Tkinter GUI (customtkinter) with interactive solving
  - ✅ CLI mode for command-line solving
  - ✅ File loader with puzzle selection
  - ✅ Real-time solution display
  - ✅ Multiple solver algorithm selection

- **Utilities**
  - ✅ Puzzle parser for standard Futoshiki input files
  - ✅ Heuristic functions for informed search
  - ✅ Solution formatting and saving
  - ✅ Comprehensive test suite

## Project Structure

```
futoshiki-solver/
├── src/
│   ├── logic/              # Logical reasoning & constraint handling
│   │   ├── axioms.py       # Axioms and constraints
│   │   ├── grounding.py    # Grounding for propositions
│   │   └── logic_utils.py  # Logic utilities
│   ├── models/             # Data structures
│   │   ├── board.py        # Puzzle board representation
│   │   ├── kb.py           # Knowledge base
│   │   └── state.py        # Search state
│   ├── solvers/            # Algorithm implementations
│   │   ├── a_star.py       # A* search with heuristics
│   │   ├── backtracking.py # Backtracking solver
│   │   ├── forward_chaining.py   # Forward chaining solver
│   │   └── backward_chaining.py  # Backward chaining solver
│   └── utils/              # Helper functions
│       ├── heuristic.py    # Heuristic functions
│       └── parser.py       # Puzzle parser
├── gui/                    # Tkinter GUI components
│   ├── app.py              # Main GUI application
│   ├── board_frame.py      # Board display
│   ├── sidebar.py          # Control sidebar
│   ├── controller.py       # MVC controller
│   ├── bridge.py           # Data format bridge
│   └── README.md           # GUI documentation
├── tests/                  # Unit tests
│   ├── test_models.py
│   ├── test_models_advanced.py
│   ├── test_forward_chaining.py
│   └── run_tests.py
├── inputs/                 # Sample puzzle inputs
├── outputs/                # Solution outputs
├── experiments/            # Experiment scripts & analysis
├── main.py                 # Entry point (GUI & CLI)
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Installation

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/futoshiki-solver.git
cd futoshiki-solver
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py  # GUI mode (default)
# or
python main.py --cli --input inputs/4x4_matrix.txt --solver backtracking  # CLI mode
```

## Usage

### GUI Mode (Interactive)
```bash
python main.py
```
Launches the modern Tkinter GUI where you can:
- Load puzzles from the inputs/ directory
- Select a solver algorithm
- Watch the solution being computed
- View results in the board display

### CLI Mode (Command Line)
```bash
python main.py --cli --input inputs/puzzle.txt --solver backtracking
```

### Available Solvers
- `backtracking` - Standard backtracking with constraint satisfaction
- `forward_chaining` - Logic programming approach
- `backward_chaining` - Logic programming approach
- `a_star` - A* search with heuristics

### CLI Options
- `--input` **(required)**: Path to input puzzle file
- `--solver` **(required)**: Solver algorithm (backtracking, forward_chaining, backward_chaining, a_star)
- `--output` **(optional)**: Path to save solution (default: outputs/)
- `--verbose` **(optional)**: Enable detailed logging

### Input Format
Puzzle files use standard Futoshiki format with numbers and inequality symbols (e.g., `<`, `>`, `^`, `v`).

## Testing

Run the test suite:
```bash
python tests/run_tests.py
# or with pytest
pytest tests/ -v
pytest tests/ --cov  # With coverage report
```

### Test Coverage
- `test_models.py` - Board and state model tests
- `test_models_advanced.py` - Advanced model tests
- `test_forward_chaining.py` - Forward chaining solver tests

## Performance & Benchmarking

Comprehensive benchmarks and performance analysis:
- See `doc/OPTIMIZATION_ANALYSIS.md` for algorithm complexity analysis
- See `benchmark.py` for running performance benchmarks
- See `experiments/` for detailed experiment scripts and results

Key documents:
- [TECHNICAL_ARCHITECTURE.md](doc/TECHNICAL_ARCHITECTURE.md) - System design
- [OPTIMIZATION_IMPLEMENTATION.md](doc/OPTIMIZATION_IMPLEMENTATION.md) - Performance optimizations
- [TEST_RESULTS.md](doc/TEST_RESULTS.md) - Test execution results

## Documentation

Comprehensive documentation available in `doc/`:
- [DOCUMENTATION_INDEX.md](doc/DOCUMENTATION_INDEX.md) - Documentation overview
- [GUI_DEVELOPMENT_GUIDE.md](doc/GUI_DEVELOPMENT_GUIDE.md) - GUI development
- [TESTING_GUIDE.md](doc/TESTING_GUIDE.md) - Testing procedures
- [QUICK_REFERENCE.md](doc/QUICK_REFERENCE.md) - Quick start reference

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python tests/run_tests.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Project Status

✅ **Active Development** - Core features implemented and tested
- All solvers functional and tested
- GUI fully operational
- CLI mode working
- Comprehensive test suite in place
