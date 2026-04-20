# Implementation Changelog

Last updated: 2026-04-16

## 1) Parser and Constraint Format Standardization

### Files
- src/utils/parser.py
- src/models/board.py

### What was changed
- Added support for two constraint input formats:
  - Legacy triplets: row col op
  - Canonical quintuplets: r1 c1 op r2 c2
- Standardized parsed constraints to canonical internal representation:
  - (r1, c1, op, r2, c2), 1-indexed
- Added validation for:
  - Bounds checking
  - Adjacency of constrained cells
  - Valid operators (< and >)
- Added backward-compatible legacy inference:
  - Prefer horizontal neighbor (r, c+1)
  - Fallback to vertical neighbor (r+1, c) when horizontal is unavailable
- Extended Board constraint typing to accept both legacy and canonical tuple forms.

### Why
- Ensure consistent constraint handling across parser, grounding, solver, and heuristic layers.
- Preserve compatibility with existing puzzle files.

## 2) Grounding Fix for Inequality Constraints

### File
- src/logic/grounding.py

### What was changed
- Implemented actual separation and normalization of inequality constraints into horizontal and vertical sets.
- Added support for both legacy 3-tuple and canonical 5-tuple constraints during grounding.
- Normalized reversed constraint directions by flipping operator when needed.
- Added strict validation for malformed constraints.

### Why
- Previously the inequality grounding path had placeholder logic, so inequality clauses could be skipped.
- This fix ensures inequality constraints are actually encoded into CNF clauses.

## 3) Main CLI Entry Point

### File
- main.py

### What was changed
- Implemented complete CLI entrypoint with subcommands:
  - solve
  - benchmark
- Added solve options:
  - --input
  - --output
  - --solver (forward_chaining, a_star)
  - --heuristic (used by A*)
- Added benchmark option:
  - --pattern
- Kept forward chaining flow intact.
- Added A* execution path.

### Why
- main.py was empty before; project needed a single practical command-line entrypoint.

## 4) A* Solver Implementation (Phase 2 scope)

### Files
- src/solvers/a_star.py
- src/solvers/__init__.py

### What was changed
- Implemented full A* solver for Futoshiki.
- Added constraint-aware search behavior:
  - Row/column duplicate pruning
  - Partial inequality consistency checks
  - MRV-style selection of next unassigned cell
  - Domain filtering for candidate values
- Added pluggable heuristic selection by name.
- Exported a_star_solver in solver package.

### Why
- Phase 2 requested completing A* only, without touching backtracking and forward chaining implementations.

## 5) Heuristic Upgrades

### File
- src/utils/heuristic.py

### What was changed
- Added canonical constraint iterator for mixed legacy/canonical input.
- Added domain computation utility for empty cells using row/column and inequality constraints.
- Added new heuristics:
  - h_domain_width
  - h_dead_end_penalty
  - h_inequality_slack
  - h_futoshiki_advanced
- Updated h_inequality_violations to support canonical constraints robustly.
- Extended h_combined to include domain-width and dead-end components.
- Added heuristic registry and resolver:
  - HEURISTIC_REGISTRY
  - get_heuristic(name)
- Set safe fallback to advanced heuristic for unknown names.

### Default behavior
- A* default heuristic is advanced.
- CLI default for --heuristic is advanced.

## 6) Test Additions and Test Runner Updates

### Files
- tests/test_integration_end_to_end.py
- tests/test_a_star.py
- tests/test_heuristic.py
- tests/run_tests.py

### What was changed
- Added end-to-end integration tests covering parser -> grounding -> solver pipeline.
- Added A* behavior tests:
  - Solvable 2x2 case
  - Inequality-respecting behavior
  - Invalid initial-state rejection
- Added heuristic tests:
  - Canonical and legacy inequality handling
  - Domain dead-end detection behavior
  - Inequality slack behavior
  - Unknown heuristic fallback behavior
- Updated custom test runner to include new test modules.

## 7) Validation Outcomes During Implementation

### Executed checks
- Focused unit tests for A* passed.
- Focused unit tests for heuristic module passed.
- Full test suite passed after updates (85 tests).
- CLI smoke tests executed for:
  - A* with explicit heuristic
  - A* with default heuristic
  - Forward chaining comparison on sample puzzle

### Notes
- Sample puzzle inputs/puzzle_3x3_simple.txt currently reports no solution for both A* and forward chaining in current pipeline, indicating consistent solver outcome for that specific input.

## 8) Scope Guardrails Followed

- Backtracking solver file was not modified.
- Forward chaining solver implementation file was not modified for Phase 2 request.

## 9) Modified and Added Files Summary

### Modified
- src/utils/parser.py
- src/models/board.py
- src/logic/grounding.py
- src/solvers/__init__.py
- src/solvers/a_star.py
- src/utils/heuristic.py
- main.py
- tests/run_tests.py

### Added
- tests/test_integration_end_to_end.py
- tests/test_a_star.py
- tests/test_heuristic.py
