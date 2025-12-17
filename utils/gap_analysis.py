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
    job_bonus: List[str] = None,
    or_groups: Dict[str, List[str]] = None
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
    if or_groups is None:
        or_groups = {}
    
    # Weights for different skill categories
    WEIGHT_REQUIRED = 1.0
    WEIGHT_PREFERRED = 0.6
    WEIGHT_BONUS = 0.3
    
    # Track which skills have been matched (to handle "or" groups)
    matched_skills = set()
    
    # Count matches using semantic similarity
    required_matched = 0
    preferred_matched = 0
    bonus_matched = 0
    
    def check_skill_match(skill: str, resume_skills: Set[str]) -> bool:
        """Check if skill matches any resume skill, including "or" group logic."""
        # Check if this skill is in an "or" group
        if skill in or_groups:
            or_group = or_groups[skill]
            # If any skill in the "or" group is already matched, this counts as matched
            if any(s in matched_skills for s in or_group):
                return True
            # Check if any skill in the "or" group matches resume
            for group_skill in or_group:
                for resume_skill in resume_skills:
                    similarity = compute_embedding_similarity(group_skill.lower(), resume_skill.lower())
                    if similarity > 0.7:
                        # Mark all skills in the "or" group as matched
                        matched_skills.update(or_group)
                        return True
        else:
            # Regular skill matching
            for resume_skill in resume_skills:
                similarity = compute_embedding_similarity(skill.lower(), resume_skill.lower())
                if similarity > 0.7:
                    matched_skills.add(skill)
                    return True
        return False
    
    # Check required skills
    for req_skill in job_required:
        if check_skill_match(req_skill, resume_skills):
            required_matched += 1
    
    # Check preferred skills
    for pref_skill in job_preferred:
        if check_skill_match(pref_skill, resume_skills):
            preferred_matched += 1
    
    # Check bonus skills
    for bonus_skill in job_bonus:
        if check_skill_match(bonus_skill, resume_skills):
            bonus_matched += 1
    
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
    job_bonus: List[str] = None,
    or_groups: Dict[str, List[str]] = None
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
    if or_groups is None:
        or_groups = {}
    
    missing = {
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }
    
    def is_skill_matched(skill: str, resume_skills: Set[str]) -> bool:
        """Check if skill is matched, including "or" group logic."""
        # Check if this skill is in an "or" group
        if skill in or_groups:
            or_group = or_groups[skill]
            # Check if any skill in the "or" group matches
            for group_skill in or_group:
                for resume_skill in resume_skills:
                    similarity = compute_embedding_similarity(group_skill.lower(), resume_skill.lower())
                    if similarity > 0.7:
                        return True  # If any skill in "or" group matches, the whole group is satisfied
            return False
        else:
            # Regular skill matching
            for resume_skill in resume_skills:
                similarity = compute_embedding_similarity(skill.lower(), resume_skill.lower())
                if similarity > 0.7:
                    return True
            return False
    
    # Check required skills
    for req_skill in job_required:
        if not is_skill_matched(req_skill, resume_skills):
            missing['HIGH'].append(req_skill)
    
    # Check preferred skills
    for pref_skill in job_preferred:
        if not is_skill_matched(pref_skill, resume_skills):
            missing['MEDIUM'].append(pref_skill)
    
    # Check bonus skills
    for bonus_skill in job_bonus:
        if not is_skill_matched(bonus_skill, resume_skills):
            missing['LOW'].append(bonus_skill)
    
    return missing


def detect_or_groups(job_description: str, all_skills: Set[str]) -> Dict[str, List[str]]:
    """
    Detect skills connected by "or" in the job description.
    
    Args:
        job_description: Job description text
        all_skills: Set of all extracted skills
        
    Returns:
        Dictionary mapping skill to list of skills in its "or" group
    """
    import re
    or_groups = {}
    job_lower = job_description.lower()
    
    # Create a mapping of lowercase skill names to actual skill names
    skill_map = {skill.lower(): skill for skill in all_skills}
    
    # Find patterns like "skill1 or skill2", "skill1/skill2", "skill1, skill2, or skill3"
    for skill in all_skills:
        skill_lower = skill.lower()
        skill_index = job_lower.find(skill_lower)
        
        if skill_index != -1:
            # Get context around the skill (300 chars before and after)
            context_start = max(0, skill_index - 300)
            context_end = min(len(job_lower), skill_index + len(skill) + 300)
            context = job_lower[context_start:context_end]
            
            or_group = [skill]
            
            # Pattern 1: "skill1 or skill2" or "skill1, skill2, or skill3"
            # Look for "or" near this skill
            or_pattern = r'\b' + re.escape(skill_lower) + r'\s+(?:,?\s*\w+\s*,?\s*)*or\s+(\w+(?:\s+\w+)*)'
            matches = re.finditer(or_pattern, context, re.IGNORECASE)
            for match in matches:
                other_skill_text = match.group(1).strip()
                # Try to find matching skill (exact or partial)
                for lower_key, actual_skill in skill_map.items():
                    if other_skill_text in lower_key or lower_key in other_skill_text:
                        if actual_skill != skill and actual_skill not in or_group:
                            or_group.append(actual_skill)
            
            # Pattern 2: "skill2 or skill1" (reverse order)
            or_pattern_reverse = r'(\w+(?:\s+\w+)*)\s+or\s+' + re.escape(skill_lower)
            matches = re.finditer(or_pattern_reverse, context, re.IGNORECASE)
            for match in matches:
                other_skill_text = match.group(1).strip()
                for lower_key, actual_skill in skill_map.items():
                    if other_skill_text in lower_key or lower_key in other_skill_text:
                        if actual_skill != skill and actual_skill not in or_group:
                            or_group.append(actual_skill)
            
            # Pattern 3: "skill1/skill2" (slash separator)
            slash_pattern = r'\b' + re.escape(skill_lower) + r'\s*/\s*(\w+(?:\s+\w+)*)'
            matches = re.finditer(slash_pattern, context, re.IGNORECASE)
            for match in matches:
                other_skill_text = match.group(1).strip()
                for lower_key, actual_skill in skill_map.items():
                    if other_skill_text in lower_key or lower_key in other_skill_text:
                        if actual_skill != skill and actual_skill not in or_group:
                            or_group.append(actual_skill)
            
            # Pattern 4: "skill2/skill1" (reverse slash)
            slash_pattern_reverse = r'(\w+(?:\s+\w+)*)\s*/\s*' + re.escape(skill_lower)
            matches = re.finditer(slash_pattern_reverse, context, re.IGNORECASE)
            for match in matches:
                other_skill_text = match.group(1).strip()
                for lower_key, actual_skill in skill_map.items():
                    if other_skill_text in lower_key or lower_key in other_skill_text:
                        if actual_skill != skill and actual_skill not in or_group:
                            or_group.append(actual_skill)
            
            if len(or_group) > 1:
                # Create bidirectional mapping - all skills in group point to the same list
                for s in or_group:
                    or_groups[s] = or_group
    
    return or_groups


def extract_skills_from_job_description(
    job_description: str,
    skill_dict: Dict[str, List[str]],
    job_templates: Dict = None
) -> Tuple[List[str], List[str], List[str], Dict[str, List[str]]]:
    """
    Extract required, preferred, and bonus skills from job description.
    Uses keyword matching and optionally job templates.
    
    Args:
        job_description: Job description text
        skill_dict: Skill dictionary
        job_templates: Optional job role templates
        
    Returns:
        Tuple of (required_skills, preferred_skills, bonus_skills, or_groups)
        or_groups: Dictionary mapping skill to list of skills in its "or" group
    """
    # Extract all skills from job description
    all_job_skills = extract_skills_from_text(job_description, skill_dict)
    
    # Detect "or" groups
    or_groups = detect_or_groups(job_description, all_job_skills)
    
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
    
    return required, preferred, bonus, or_groups

