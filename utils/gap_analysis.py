"""
Gap analysis utilities using SBERT embeddings and weighted scoring.
Identifies missing skills and categorizes them by priority.
"""

import json
import os
from typing import Dict, List, Set, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Import skill extraction for job description parsing
try:
    from .skill_extraction import extract_skills_from_text
except ImportError:
    from skill_extraction import extract_skills_from_text


# Global model variable (lazy loading)
_model = None


def load_sentence_transformer():
    """Load SBERT model (lazy loading for performance)."""
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def load_job_role_templates(file_path: str = "data/job_role_templates.json") -> Dict:
    """
    Load job role templates from JSON file.
    
    Args:
        file_path: Path to job role templates JSON file
        
    Returns:
        Dictionary of job role templates
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Job role templates not found at {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in job role templates at {file_path}")


def compute_embedding_similarity(skill1: str, skill2: str) -> float:
    """
    Compute semantic similarity between two skills using SBERT embeddings.
    
    Args:
        skill1: First skill name
        skill2: Second skill name
        
    Returns:
        Similarity score between 0 and 1
    """
    model = load_sentence_transformer()
    embeddings = model.encode([skill1, skill2])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    # Normalize to 0-1 range (cosine similarity is already -1 to 1, but typically 0 to 1 for normalized vectors)
    return max(0.0, min(1.0, (similarity + 1) / 2))


def weighted_match_score(
    resume_skills: Set[str],
    job_required: List[str],
    job_preferred: List[str] = None,
    job_bonus: List[str] = None
) -> Tuple[float, Dict[str, any]]:
    """
    Compute weighted match score between resume skills and job requirements.
    
    Args:
        resume_skills: Set of skills found in resume
        job_required: List of required skills
        job_preferred: List of preferred skills (optional)
        job_bonus: List of bonus skills (optional)
        
    Returns:
        Tuple of (match_score, details_dict)
        details_dict contains: required_match, preferred_match, bonus_match, total_possible
    """
    if job_preferred is None:
        job_preferred = []
    if job_bonus is None:
        job_bonus = []
    
    # Weights for different skill categories
    WEIGHT_REQUIRED = 1.0
    WEIGHT_PREFERRED = 0.6
    WEIGHT_BONUS = 0.3
    
    # Count matches using semantic similarity
    required_matched = 0
    preferred_matched = 0
    bonus_matched = 0
    
    # Check required skills
    for req_skill in job_required:
        for resume_skill in resume_skills:
            similarity = compute_embedding_similarity(req_skill.lower(), resume_skill.lower())
            if similarity > 0.7:  # Threshold for match
                required_matched += 1
                break
    
    # Check preferred skills
    for pref_skill in job_preferred:
        for resume_skill in resume_skills:
            similarity = compute_embedding_similarity(pref_skill.lower(), resume_skill.lower())
            if similarity > 0.7:
                preferred_matched += 1
                break
    
    # Check bonus skills
    for bonus_skill in job_bonus:
        for resume_skill in resume_skills:
            similarity = compute_embedding_similarity(bonus_skill.lower(), resume_skill.lower())
            if similarity > 0.7:
                bonus_matched += 1
                break
    
    # Calculate weighted score
    total_required = len(job_required) if job_required else 1
    total_preferred = len(job_preferred) if job_preferred else 1
    total_bonus = len(job_bonus) if job_bonus else 1
    
    required_score = (required_matched / total_required) * WEIGHT_REQUIRED
    preferred_score = (preferred_matched / total_preferred) * WEIGHT_PREFERRED if job_preferred else 0
    bonus_score = (bonus_matched / total_bonus) * WEIGHT_BONUS if job_bonus else 0
    
    # Normalize by total possible weight
    total_weight = WEIGHT_REQUIRED + (WEIGHT_PREFERRED if job_preferred else 0) + (WEIGHT_BONUS if job_bonus else 0)
    match_score = (required_score + preferred_score + bonus_score) / total_weight if total_weight > 0 else 0.0
    
    details = {
        'required_match': required_matched,
        'required_total': total_required,
        'preferred_match': preferred_matched,
        'preferred_total': total_preferred,
        'bonus_match': bonus_matched,
        'bonus_total': total_bonus,
        'score': match_score
    }
    
    return match_score, details


def find_missing_skills(
    resume_skills: Set[str],
    job_required: List[str],
    job_preferred: List[str] = None,
    job_bonus: List[str] = None
) -> Dict[str, List[str]]:
    """
    Find missing skills categorized by priority.
    
    Args:
        resume_skills: Set of skills found in resume
        job_required: List of required skills
        job_preferred: List of preferred skills (optional)
        job_bonus: List of bonus skills (optional)
        
    Returns:
        Dictionary with keys 'HIGH', 'MEDIUM', 'LOW' mapping to lists of missing skills
    """
    if job_preferred is None:
        job_preferred = []
    if job_bonus is None:
        job_bonus = []
    
    missing = {
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }
    
    # Check required skills
    for req_skill in job_required:
        found = False
        for resume_skill in resume_skills:
            similarity = compute_embedding_similarity(req_skill.lower(), resume_skill.lower())
            if similarity > 0.7:
                found = True
                break
        if not found:
            missing['HIGH'].append(req_skill)
    
    # Check preferred skills
    for pref_skill in job_preferred:
        found = False
        for resume_skill in resume_skills:
            similarity = compute_embedding_similarity(pref_skill.lower(), resume_skill.lower())
            if similarity > 0.7:
                found = True
                break
        if not found:
            missing['MEDIUM'].append(pref_skill)
    
    # Check bonus skills
    for bonus_skill in job_bonus:
        found = False
        for resume_skill in resume_skills:
            similarity = compute_embedding_similarity(bonus_skill.lower(), resume_skill.lower())
            if similarity > 0.7:
                found = True
                break
        if not found:
            missing['LOW'].append(bonus_skill)
    
    return missing


def extract_skills_from_job_description(
    job_description: str,
    skill_dict: Dict[str, List[str]],
    job_templates: Dict = None
) -> Tuple[List[str], List[str], List[str]]:
    """
    Extract required, preferred, and bonus skills from job description.
    Uses keyword matching and optionally job templates.
    
    Args:
        job_description: Job description text
        skill_dict: Skill dictionary
        job_templates: Optional job role templates
        
    Returns:
        Tuple of (required_skills, preferred_skills, bonus_skills)
    """
    # Extract all skills from job description
    all_job_skills = extract_skills_from_text(job_description, skill_dict)
    
    # Try to categorize based on keywords in job description
    job_lower = job_description.lower()
    required = []
    preferred = []
    bonus = []
    
    # Keywords that indicate required skills
    required_keywords = ['required', 'must have', 'must possess', 'essential', 'mandatory', 'necessary']
    # Keywords that indicate preferred skills
    preferred_keywords = ['preferred', 'nice to have', 'desired', 'advantage', 'plus', 'bonus']
    
    for skill in all_job_skills:
        # Find skill in context
        skill_lower = skill.lower()
        skill_index = job_lower.find(skill_lower)
        
        if skill_index != -1:
            # Check context around skill
            context_start = max(0, skill_index - 100)
            context_end = min(len(job_lower), skill_index + len(skill) + 100)
            context = job_lower[context_start:context_end]
            
            # Check for required keywords
            is_required = any(keyword in context for keyword in required_keywords)
            is_preferred = any(keyword in context for keyword in preferred_keywords)
            
            if is_required:
                required.append(skill)
            elif is_preferred:
                preferred.append(skill)
            else:
                bonus.append(skill)
        else:
            # Default to bonus if context unclear
            bonus.append(skill)
    
    # If no skills found in required/preferred, put all in required
    if not required and not preferred and all_job_skills:
        required = list(all_job_skills)
    
    return required, preferred, bonus

