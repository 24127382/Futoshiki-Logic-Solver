# Requirements Installation Guide

## Overview

The Futoshiki Solver is designed to have **minimal dependencies** by using only Python's standard library for core functionality.

## Dependency Tiers

### Tier 1: Core (No External Dependencies)
The core solver requires **only Python 3.8+** and uses exclusively standard library modules:
- `typing` (type hints)
- `unittest` (testing framework)

**Installation**:
```bash
# No external packages needed, just Python 3.8+
python --version  # Verify Python version
```

---

### Tier 2: Development (Optional)
For development, testing, and code quality:

```bash
pip install -r requirements-dev.txt
```

**Includes**:
- `pytest` - Testing framework
- `black` - Code formatter
- `flake8` - Linter  
- `mypy` - Type checker
- `coverage` - Test coverage reporting

**Usage**:
```bash
# Run tests
python -m pytest experiments/ -v

# Run tests with coverage
coverage run -m pytest experiments/
coverage report

# Format code
black src/

# Check code style
flake8 src/

# Type checking
mypy src/
```

---

### Tier 3: Optional Features
For advanced features like SAT solver integration and visualization:

```bash
pip install -r requirements-optional.txt
```

**Includes**:
- **SAT Solvers**: `z3-solver`, `python-sat`, `pysmt`
- **Visualization**: `matplotlib`, `seaborn`, `numpy`, `scipy`
- **GUI Frameworks**: `PyQt6` (alternative to tkinter)

**Usage Example** (with Z3):
```python
from z3 import *
# Use Z3 for constraint solving
```

---

## Installation Scenarios

### Scenario 1: Quick Test (Minimal)
```bash
# Just run the core solver without external dependencies
python -m unittest experiments.test_models -v
```
✅ **No pip install needed**

### Scenario 2: Development Setup
```bash
# Install development tools
pip install -r requirements-dev.txt

# Run all tests with coverage
coverage run -m pytest experiments/ -v
coverage report

# Format code
black src/
```

### Scenario 3: Complete Setup
```bash
# Install everything
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -r requirements-optional.txt

# Or all in one:
pip install -r requirements-dev.txt -r requirements-optional.txt
```

### Scenario 4: Specific SAT Solver
```bash
# Just Z3
pip install z3-solver

# Or python-sat
pip install python-sat

# Or both
pip install z3-solver python-sat
```

---

## Version Requirements

| Component | Version | Required? |
|-----------|---------|-----------|
| Python | ≥ 3.8 | ✅ Yes |
| pytest | ≥ 7.0 | ❌ Optional (dev) |
| black | ≥ 23.0 | ❌ Optional (dev) |
| z3-solver | ≥ 4.12 | ❌ Optional (SAT) |

---

## Verifying Installation

### Check Python Version
```bash
python --version
# Should output: Python 3.8.0 or higher
```

### Check Core Installation
```bash
# Run core tests (no external dependencies)
python -m unittest experiments.test_models -v
```

### Check Development Tools
```bash
# If pytest installed
pip show pytest
pytest --version

# If black installed
pip show black
black --version
```

### Check SAT Solver Integration
```bash
# If z3 installed
python -c "import z3; print(z3.get_version_string())"

# If python-sat installed
python -c "from pysat.solvers import Cadical; print('python-sat OK')"
```

---

## Dependency Graph

```
futoshiki-solver/
├── Core (Standard Library Only)
│   ├── typing
│   ├── unittest
│   └── collections
│
├── Development (Optional - requirements-dev.txt)
│   ├── pytest
│   ├── pytest-cov
│   ├── black
│   ├── flake8
│   └── mypy
│
└── Advanced/Optional (Optional - requirements-optional.txt)
    ├── SAT Solvers
    │   ├── z3-solver
    │   ├── python-sat
    │   └── pysmt
    ├── Visualization
    │   ├── matplotlib
    │   ├── numpy
    │   └── scipy
    └── GUI
        ├── PyQt6
        └── PySimpleGUI
```

---

## Troubleshooting

### ImportError: No module named 'z3'
**Solution**: Install Z3 SAT solver
```bash
pip install z3-solver
```

### ImportError: No module named 'pytest'
**Solution**: Install development dependencies
```bash
pip install -r requirements-dev.txt
```

### ModuleNotFoundError on tkinter
**Solution**: Install tkinter (OS-specific)
- **Windows**: Comes with Python, use official installer
- **macOS**: `brew install python-tkinter`
- **Linux**: `apt-get install python3-tk`

---

## Contributing

To set up your environment for development:

```bash
# Clone the repository
git clone https://github.com/yourusername/futoshiki-solver.git
cd futoshiki-solver

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install all dependencies
pip install -r requirements-dev.txt
pip install -r requirements-optional.txt

# Verify setup
python -m pytest experiments/ -v
black --check src/
```

---

## Performance Notes

- **Core solver**: Fast, no external overhead
- **With Z3**: Better performance for large puzzles (9×9+)
- **Memory**: Minimal core; Z3 uses more for complex formulas
- **CPU**: Single-threaded by default; SAT solvers may use multiple cores

---

## Summary

| Task | Required | Command |
|------|----------|---------|
| Run core solver | Python 3.8+ | `python main.py` |
| Run tests | Python 3.8+ | `python -m unittest ...` |
| Development | + dev deps | `pip install -r requirements-dev.txt` |
| SAT integration | + optional deps | `pip install z3-solver` |
| Full setup | All | `pip install -r requirements-dev.txt requirements-optional.txt` |

---

**Last Updated**: April 2026  
**Tested With**: Python 3.8, 3.9, 3.10, 3.11
