"""
Prescriptive optimization module for skill learning.
Uses integer linear programming to find optimal skill learning sequence
that maximizes job match score improvement under time and budget constraints.
"""

from typing import Dict, List, Tuple, Optional
import re

try:
    from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus, value
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False

# Try scipy as fallback
try:
    from scipy.optimize import linprog
    import numpy as np
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


# Skill complexity and cost estimates
COMPLEX_SKILLS = {
    'machine learning', 'data science', 'cloud architecture', 'devops', 
    'full stack', 'deep learning', 'natural language processing', 
    'computer vision', 'kubernetes', 'microservices', 'distributed systems'
}

# Base estimates (can be customized)
BASE_TIME_ESTIMATES = {
    'HIGH': {'simple': 0.5, 'complex': 2.0},  # months
    'MEDIUM': {'simple': 0.25, 'complex': 1.0},
    'LOW': {'simple': 0.125, 'complex': 0.5}
}

BASE_COST_ESTIMATES = {
    'HIGH': {'simple': 50, 'complex': 200},  # dollars
    'MEDIUM': {'simple': 30, 'complex': 150},
    'LOW': {'simple': 20, 'complex': 100}
}

# Score weights (same as gap_analysis.py)
WEIGHT_REQUIRED = 1.0
WEIGHT_PREFERRED = 0.6
WEIGHT_BONUS = 0.3


def estimate_skill_time(skill: str, priority: str) -> float:
    """
    Estimate learning time in months for a skill.
    
    Args:
        skill: Skill name
        priority: Priority level (HIGH, MEDIUM, LOW)
        
    Returns:
        Estimated time in months
    """
    skill_lower = skill.lower()
    is_complex = any(complex_term in skill_lower for complex_term in COMPLEX_SKILLS)
    
    complexity = 'complex' if is_complex else 'simple'
    return BASE_TIME_ESTIMATES.get(priority, BASE_TIME_ESTIMATES['MEDIUM'])[complexity]


def estimate_skill_cost(skill: str, priority: str) -> float:
    """
    Estimate learning cost in dollars for a skill.
    
    Args:
        skill: Skill name
        priority: Priority level (HIGH, MEDIUM, LOW)
        
    Returns:
        Estimated cost in dollars
    """
    skill_lower = skill.lower()
    is_complex = any(complex_term in skill_lower for complex_term in COMPLEX_SKILLS)
    
    complexity = 'complex' if is_complex else 'simple'
    return BASE_COST_ESTIMATES.get(priority, BASE_COST_ESTIMATES['MEDIUM'])[complexity]


def get_skill_score_weight(priority: str) -> float:
    """
    Get score weight for a skill based on priority.
    
    Args:
        priority: Priority level (HIGH, MEDIUM, LOW)
        
    Returns:
        Score weight
    """
    weights = {
        'HIGH': WEIGHT_REQUIRED,
        'MEDIUM': WEIGHT_PREFERRED,
        'LOW': WEIGHT_BONUS
    }
    return weights.get(priority, WEIGHT_PREFERRED)


def optimize_skill_learning_pulp(
    missing_skills: Dict[str, List[str]],
    time_budget_months: float,
    cost_budget_dollars: float,
    weight_required: float = 1.0,
    weight_preferred: float = 0.6,
    weight_bonus: float = 0.3
) -> Tuple[Dict[str, List[str]], Dict[str, float], float, str]:
    """
    Optimize skill learning using PuLP (Integer Linear Programming).
    
    Args:
        missing_skills: Dictionary with HIGH, MEDIUM, LOW priority skills
        time_budget_months: Maximum time available in months
        cost_budget_dollars: Maximum budget in dollars
        weight_required: Weight for required skills in objective function (default: 1.0)
        weight_preferred: Weight for preferred skills in objective function (default: 0.6)
        weight_bonus: Weight for bonus skills in objective function (default: 0.3)
        
    Returns:
        Tuple of (selected_skills_dict, skill_details, objective_value, status)
        selected_skills_dict: Dictionary mapping priority to list of selected skills
        skill_details: Dictionary with time, cost, and score for each selected skill
        objective_value: Maximum score improvement achieved
        status: Optimization status message
    """
    if not PULP_AVAILABLE:
        raise ImportError("PuLP is required for optimization. Install with: pip install pulp")
    
    # Create problem
    prob = LpProblem("Skill_Learning_Optimization", LpMaximize)
    
    # Collect all skills with their metadata
    all_skills = []
    skill_vars = {}
    skill_metadata = {}
    
    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        for skill in missing_skills.get(priority, []):
            skill_id = f"{priority}_{skill}"
            all_skills.append((priority, skill, skill_id))
            
            # Create binary variable (1 = learn, 0 = skip)
            skill_vars[skill_id] = LpVariable(skill_id, cat='Binary')
            
            # Store metadata
            time_est = estimate_skill_time(skill, priority)
            cost_est = estimate_skill_cost(skill, priority)
            # Use custom weights if provided
            if priority == 'HIGH':
                score_weight = weight_required
            elif priority == 'MEDIUM':
                score_weight = weight_preferred
            else:  # LOW
                score_weight = weight_bonus
            
            skill_metadata[skill_id] = {
                'priority': priority,
                'skill': skill,
                'time': time_est,
                'cost': cost_est,
                'score_weight': score_weight
            }
    
    if not all_skills:
        return ({'HIGH': [], 'MEDIUM': [], 'LOW': []}, {}, 0.0, "No missing skills to optimize")
    
    # Objective: Maximize weighted score improvement
    prob += lpSum([
        skill_vars[skill_id] * skill_metadata[skill_id]['score_weight']
        for _, _, skill_id in all_skills
    ]), "Total_Score_Improvement"
    
    # Constraint 1: Time budget
    prob += lpSum([
        skill_vars[skill_id] * skill_metadata[skill_id]['time']
        for _, _, skill_id in all_skills
    ]) <= time_budget_months, "Time_Budget"
    
    # Constraint 2: Cost budget
    prob += lpSum([
        skill_vars[skill_id] * skill_metadata[skill_id]['cost']
        for _, _, skill_id in all_skills
    ]) <= cost_budget_dollars, "Cost_Budget"
    
    # Solve
    prob.solve()
    
    # Extract results
    selected_skills = {'HIGH': [], 'MEDIUM': [], 'LOW': []}
    skill_details = {}
    objective_value = 0.0
    
    for priority, skill, skill_id in all_skills:
        if skill_vars[skill_id].varValue == 1:
            selected_skills[priority].append(skill)
            skill_details[skill] = {
                'priority': priority,
                'time_months': skill_metadata[skill_id]['time'],
                'cost_dollars': skill_metadata[skill_id]['cost'],
                'score_weight': skill_metadata[skill_id]['score_weight']
            }
            objective_value += skill_metadata[skill_id]['score_weight']
    
    status_msg = f"Optimization Status: {LpStatus[prob.status]}"
    if prob.status == 1:  # Optimal
        status_msg += f" | Optimal solution found. Score improvement: {objective_value:.2f}"
    elif prob.status == 0:  # Not solved
        status_msg += " | Problem not solved"
    elif prob.status == -1:  # Infeasible
        status_msg += " | No feasible solution exists (constraints too tight)"
    elif prob.status == -2:  # Unbounded
        status_msg += " | Problem is unbounded"
    
    return selected_skills, skill_details, objective_value, status_msg


def optimize_skill_learning_scipy(
    missing_skills: Dict[str, List[str]],
    time_budget_months: float,
    cost_budget_dollars: float,
    weight_required: float = 1.0,
    weight_preferred: float = 0.6,
    weight_bonus: float = 0.3
) -> Tuple[Dict[str, List[str]], Dict[str, float], float, str]:
    """
    Optimize skill learning using scipy.optimize (fallback if PuLP unavailable).
    Note: This uses continuous relaxation, results may need rounding.
    
    Args:
        missing_skills: Dictionary with HIGH, MEDIUM, LOW priority skills
        time_budget_months: Maximum time available in months
        cost_budget_dollars: Maximum budget in dollars
        weight_required: Weight for required skills in objective function (default: 1.0)
        weight_preferred: Weight for preferred skills in objective function (default: 0.6)
        weight_bonus: Weight for bonus skills in objective function (default: 0.3)
        
    Returns:
        Tuple of (selected_skills_dict, skill_details, objective_value, status)
    """
    if not SCIPY_AVAILABLE:
        raise ImportError("scipy is required for optimization. Install with: pip install scipy")
    
    # Collect all skills with their metadata
    all_skills = []
    skill_metadata = {}
    
    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        for skill in missing_skills.get(priority, []):
            skill_id = f"{priority}_{skill}"
            all_skills.append((priority, skill, skill_id))
            
            time_est = estimate_skill_time(skill, priority)
            cost_est = estimate_skill_cost(skill, priority)
            # Use custom weights if provided
            if priority == 'HIGH':
                score_weight = weight_required
            elif priority == 'MEDIUM':
                score_weight = weight_preferred
            else:  # LOW
                score_weight = weight_bonus
            
            skill_metadata[skill_id] = {
                'priority': priority,
                'skill': skill,
                'time': time_est,
                'cost': cost_est,
                'score_weight': score_weight
            }
    
    if not all_skills:
        return ({'HIGH': [], 'MEDIUM': [], 'LOW': []}, {}, 0.0, "No missing skills to optimize")
    
    n_skills = len(all_skills)
    
    # Objective: Maximize weighted score (negate for minimization)
    c = np.array([-skill_metadata[skill_id]['score_weight'] for _, _, skill_id in all_skills])
    
    # Constraints: Ax <= b
    # Time constraint
    time_coeffs = np.array([skill_metadata[skill_id]['time'] for _, _, skill_id in all_skills])
    # Cost constraint
    cost_coeffs = np.array([skill_metadata[skill_id]['cost'] for _, _, skill_id in all_skills])
    
    A_ub = np.vstack([time_coeffs, cost_coeffs])
    b_ub = np.array([time_budget_months, cost_budget_dollars])
    
    # Bounds: 0 <= x <= 1 (continuous relaxation)
    bounds = [(0, 1)] * n_skills
    
    # Solve
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    
    # Round results (simple heuristic: select if x > 0.5)
    selected_skills = {'HIGH': [], 'MEDIUM': [], 'LOW': []}
    skill_details = {}
    objective_value = 0.0
    
    if result.success:
        for i, (priority, skill, skill_id) in enumerate(all_skills):
            if result.x[i] > 0.5:  # Threshold for selection
                selected_skills[priority].append(skill)
                skill_details[skill] = {
                    'priority': priority,
                    'time_months': skill_metadata[skill_id]['time'],
                    'cost_dollars': skill_metadata[skill_id]['cost'],
                    'score_weight': skill_metadata[skill_id]['score_weight']
                }
                objective_value += skill_metadata[skill_id]['score_weight']
        
        status_msg = f"Optimization Status: Success (scipy continuous relaxation)"
        status_msg += f" | Score improvement: {objective_value:.2f}"
    else:
        status_msg = f"Optimization Status: Failed - {result.message}"
    
    return selected_skills, skill_details, objective_value, status_msg


def optimize_skill_learning(
    missing_skills: Dict[str, List[str]],
    time_budget_months: float,
    cost_budget_dollars: float,
    weight_required: float = 1.0,
    weight_preferred: float = 0.6,
    weight_bonus: float = 0.3
) -> Tuple[Dict[str, List[str]], Dict[str, float], float, str]:
    """
    Optimize skill learning sequence to maximize job match score improvement.
    Automatically selects best available solver (PuLP preferred, scipy fallback).
    
    Args:
        missing_skills: Dictionary with HIGH, MEDIUM, LOW priority skills
        time_budget_months: Maximum time available in months
        cost_budget_dollars: Maximum budget in dollars
        weight_required: Weight for required skills in objective function (default: 1.0)
        weight_preferred: Weight for preferred skills in objective function (default: 0.6)
        weight_bonus: Weight for bonus skills in objective function (default: 0.3)
        
    Returns:
        Tuple of (selected_skills_dict, skill_details, objective_value, status)
        selected_skills_dict: Dictionary mapping priority to list of selected skills
        skill_details: Dictionary with time, cost, and score for each selected skill
        objective_value: Maximum score improvement achieved
        status: Optimization status message
    """
    if PULP_AVAILABLE:
        return optimize_skill_learning_pulp(missing_skills, time_budget_months, cost_budget_dollars, 
                                            weight_required, weight_preferred, weight_bonus)
    elif SCIPY_AVAILABLE:
        return optimize_skill_learning_scipy(missing_skills, time_budget_months, cost_budget_dollars,
                                             weight_required, weight_preferred, weight_bonus)
    else:
        raise ImportError(
            "No optimization library available. Install PuLP (recommended) or scipy:\n"
            "  pip install pulp\n"
            "  or\n"
            "  pip install scipy"
        )


def calculate_expected_score_improvement(
    selected_skills: Dict[str, List[str]],
    current_match_details: Dict,
    job_required: List[str],
    job_preferred: List[str],
    job_bonus: List[str]
) -> Dict[str, float]:
    """
    Calculate expected match score improvement after learning selected skills.
    
    Args:
        selected_skills: Dictionary of selected skills by priority
        current_match_details: Current match details from gap_analysis
        job_required: List of required job skills
        job_preferred: List of preferred job skills
        job_bonus: List of bonus job skills
        
    Returns:
        Dictionary with expected improvements
    """
    # Current counts
    current_required = current_match_details.get('required_match', 0)
    current_preferred = current_match_details.get('preferred_match', 0)
    current_bonus = current_match_details.get('bonus_match', 0)
    
    total_required = current_match_details.get('required_total', len(job_required) if job_required else 1)
    total_preferred = current_match_details.get('preferred_total', len(job_preferred) if job_preferred else 1)
    total_bonus = current_match_details.get('bonus_total', len(job_bonus) if job_bonus else 1)
    
    # Count new skills that will be learned
    new_required = len([s for s in selected_skills.get('HIGH', []) if s in job_required])
    new_preferred = len([s for s in selected_skills.get('MEDIUM', []) if s in job_preferred])
    new_bonus = len([s for s in selected_skills.get('LOW', []) if s in job_bonus])
    
    # Calculate new scores
    new_required_count = min(current_required + new_required, total_required)
    new_preferred_count = min(current_preferred + new_preferred, total_preferred)
    new_bonus_count = min(current_bonus + new_bonus, total_bonus)
    
    required_score_new = (new_required_count / total_required) * WEIGHT_REQUIRED if total_required > 0 else 0
    preferred_score_new = (new_preferred_count / total_preferred) * WEIGHT_PREFERRED if total_preferred > 0 else 0
    bonus_score_new = (new_bonus_count / total_bonus) * WEIGHT_BONUS if total_bonus > 0 else 0
    
    total_weight = WEIGHT_REQUIRED + (WEIGHT_PREFERRED if job_preferred else 0) + (WEIGHT_BONUS if job_bonus else 0)
    new_match_score = (required_score_new + preferred_score_new + bonus_score_new) / total_weight if total_weight > 0 else 0.0
    
    current_match_score = current_match_details.get('score', 0.0)
    score_improvement = new_match_score - current_match_score
    
    return {
        'current_score': current_match_score,
        'expected_score': new_match_score,
        'score_improvement': score_improvement,
        'new_required_matched': new_required_count,
        'new_preferred_matched': new_preferred_count,
        'new_bonus_matched': new_bonus_count
    }

