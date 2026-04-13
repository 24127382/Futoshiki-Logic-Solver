"""Utility functions for logical reasoning and SAT-related operations.

Provides optimizations and analysis tools for CNF clause manipulation.
"""

from typing import List, Set, Tuple, Dict
from src.models.kb import KnowledgeBase


def remove_tautologies(clauses: List[List[int]]) -> List[List[int]]:
    """Remove tautological clauses from a list.
    
    A tautology is a clause containing both p and -p for some variable p.
    These clauses are always satisfied and can be removed.
    
    Args:
        clauses: List of clauses (each clause is a list of literals)
        
    Returns:
        List with tautologies removed
    """
    result = []
    
    for clause in clauses:
        # Check if clause contains both p and -p
        literal_set = set(clause)
        is_tautology = False
        
        for lit in literal_set:
            if -lit in literal_set:
                is_tautology = True
                break
        
        if not is_tautology:
            result.append(clause)
    
    return result


def remove_duplicates(clauses: List[List[int]]) -> List[List[int]]:
    """Remove duplicate clauses and standardize clause representation.
    
    Args:
        clauses: List of clauses
        
    Returns:
        List with duplicates removed (uses sorted tuples for comparison)
    """
    seen = set()
    result = []
    
    for clause in clauses:
        # Normalize clause as sorted tuple for comparison
        normalized = tuple(sorted(set(clause)))
        if normalized not in seen:
            seen.add(normalized)
            result.append(list(normalized))
    
    return result


def unit_clauses_to_literals(clauses: List[List[int]]) -> List[int]:
    """Extract all unit clauses (single-literal clauses) into a list.
    
    Args:
        clauses: List of clauses
        
    Returns:
        List of literals from unit clauses
    """
    return [clause[0] for clause in clauses if len(clause) == 1]


def pure_literal_elimination(clauses: List[List[int]]) -> Dict[int, bool]:
    """Find pure literals and their assignments via pure literal elimination.
    
    A pure literal is one that appears with only one polarity across all clauses.
    
    **Note:** In practice, unit propagation usually finds these first.
    
    Args:
        clauses: List of clauses
        
    Returns:
        Dict of {literal: assignment} for pure literals
    """
    # Collect all literals and their polarities
    literal_polarities = {}
    
    for clause in clauses:
        for lit in clause:
            if lit not in literal_polarities:
                literal_polarities[lit] = {'positive': False, 'negative': False}
            
            if lit > 0:
                literal_polarities[lit]['positive'] = True
            else:
                literal_polarities[lit]['negative'] = True
    
    # Find pure literals (appear with only one polarity)
    pure_assignments = {}
    for abs_lit in set(abs(lit) for lit in literal_polarities.keys()):
        if abs_lit in literal_polarities:
            pol = literal_polarities[abs_lit]
        else:
            # Check both positive and negative
            pol_pos = literal_polarities.get(abs_lit, {}).get('positive', False)
            pol_neg = literal_polarities.get(-abs_lit, {}).get('negative', False)
            pol = {'positive': pol_pos, 'negative': pol_neg}
        
        # If appears only as positive
        if pol.get('positive', False) and not pol.get('negative', False):
            pure_assignments[abs_lit] = True
        # If appears only as negative
        elif not pol.get('positive', False) and pol.get('negative', False):
            pure_assignments[abs_lit] = False
    
    return pure_assignments


def subsume_clauses(clauses: List[List[int]]) -> List[List[int]]:
    """Remove subsumed clauses.
    
    Clause C1 subsumes C2 if all literals in C1 are in C2 (C1 ⊆ C2).
    We can remove C2 because C1 is stronger.
    
    **Warning:** This is O(n²) and can be slow for large clause sets.
    
    Args:
        clauses: List of clauses
        
    Returns:
        List with subsumed clauses removed
    """
    # Convert to sets for easier comparison
    clause_sets = [set(clause) for clause in clauses]
    result_indices = set(range(len(clause_sets)))
    
    # Check each pair for subsumption
    for i in range(len(clause_sets)):
        if i not in result_indices:
            continue
        
        for j in range(len(clause_sets)):
            if i == j or j not in result_indices:
                continue
            
            # If clause i subsumes clause j, remove j
            if clause_sets[i] <= clause_sets[j] and clause_sets[i] != clause_sets[j]:
                result_indices.discard(j)
    
    return [clauses[i] for i in sorted(result_indices)]


def unit_propagation_fast(clauses: List[List[int]]) -> Tuple[List[List[int]], Dict[int, bool]]:
    """Fast unit propagation algorithm.
    
    Repeatedly:
    1. Find unit clauses (single literal)
    2. Assign the literal to true
    3. Remove all clauses containing that literal
    4. Remove negation of that literal from all other clauses
    
    Repeat until no more unit clauses or contradiction found.
    
    Args:
        clauses: List of clauses
        
    Returns:
        Tuple of (remaining_clauses, assignments)
        where assignments maps variables to their forced values
    """
    # Make a mutable copy
    remaining = [list(clause) for clause in clauses]
    assignments = {}
    
    changed = True
    while changed:
        changed = False
        
        # Find unit clauses
        unit_clause_index = -1
        for i, clause in enumerate(remaining):
            if len(clause) == 0:
                # Empty clause - unsatisfiable
                return [], None
            elif len(clause) == 1:
                unit_clause_index = i
                break
        
        if unit_clause_index == -1:
            break  # No more unit clauses
        
        # Get the unit literal
        unit_lit = remaining[unit_clause_index][0]
        assignments[abs(unit_lit)] = (unit_lit > 0)
        changed = True
        
        # Remove clauses satisfied by this literal and simplify others
        simplified = []
        for clause in remaining:
            if unit_lit in clause:
                # This clause is satisfied, skip it
                continue
            elif -unit_lit in clause:
                # Remove the negation of unit_lit
                new_clause = [lit for lit in clause if lit != -unit_lit]
                if new_clause:  # Only keep non-empty clauses
                    simplified.append(new_clause)
            else:
                # Keep clause as is
                simplified.append(clause)
        
        remaining = simplified
    
    return remaining, assignments if assignments else {}


def estimate_clause_reduction(kb: KnowledgeBase) -> Dict[str, int]:
    """Estimate how much unit propagation could reduce the clause set.
    
    Args:
        kb: Knowledge base with clauses
        
    Returns:
        Dict with statistics about potential reduction
    """
    stats = {
        'total_clauses': len(kb.clauses),
        'unit_clauses': len(kb.clauses_by_length.get(1, [])),
        'binary_clauses': len(kb.clauses_by_length.get(2, [])),
        'horn_clauses': 0,  # Clauses with at most 1 positive literal
        'pure_literals': 0,
    }
    
    # Count horn clauses
    for clause in kb.clauses:
        positive_count = sum(1 for lit in clause if lit > 0)
        if positive_count <= 1:
            stats['horn_clauses'] += 1
    
    return stats
