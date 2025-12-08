"""
Skill extraction utilities using keyword matching.
Loads skill dictionary and performs case-insensitive matching.
"""

import json
import os
from typing import Set, List, Dict
import re


def load_skill_dictionary(file_path: str = "data/skill_dictionary.json") -> Dict[str, List[str]]:
    """
    Load skill dictionary from JSON file.
    
    Args:
        file_path: Path to skill dictionary JSON file
        
    Returns:
        Dictionary mapping skill categories to skill lists
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Skill dictionary not found at {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in skill dictionary at {file_path}")


def normalize_skill_name(skill: str) -> str:
    """
    Normalize skill name for comparison (lowercase, remove special chars).
    
    Args:
        skill: Skill name to normalize
        
    Returns:
        Normalized skill name
    """
    # Convert to lowercase and remove extra spaces
    normalized = skill.lower().strip()
    # Remove common prefixes/suffixes that don't affect matching
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized


def build_skill_patterns(skill_dict: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Build regex patterns for all skills in dictionary.
    
    Args:
        skill_dict: Skill dictionary
        
    Returns:
        Dictionary mapping normalized skill names to original skill names
    """
    skill_map = {}
    
    for category, skills in skill_dict.items():
        for skill in skills:
            normalized = normalize_skill_name(skill)
            # Store mapping: normalized -> original
            if normalized not in skill_map:
                skill_map[normalized] = skill
            # Also handle variations (e.g., "MS Excel" -> "Excel")
            # Extract base skill name if it contains common prefixes
            base_skill = re.sub(r'^(ms|microsoft|adobe|google)\s+', '', normalized)
            if base_skill != normalized and base_skill not in skill_map:
                skill_map[base_skill] = skill
    
    return skill_map


def extract_skills_from_text(text: str, skill_dict: Dict[str, List[str]]) -> Set[str]:
    """
    Extract skills from text using keyword matching.
    
    Args:
        text: Text to search for skills
        skill_dict: Skill dictionary
        
    Returns:
        Set of unique skill names found
    """
    if not text:
        return set()
    
    text_lower = text.lower()
    skill_map = build_skill_patterns(skill_dict)
    found_skills = set()
    
    # Check for each skill in the text
    for normalized_skill, original_skill in skill_map.items():
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(normalized_skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(original_skill)
    
    # Also check for direct matches in original case
    for category, skills in skill_dict.items():
        for skill in skills:
            # Case-insensitive search with word boundaries
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                found_skills.add(skill)
    
    return found_skills


def normalize_duplicates(skills: Set[str]) -> Set[str]:
    """
    Normalize duplicate skills (e.g., "MS Excel" and "Excel" -> "Excel").
    
    Args:
        skills: Set of skill names
        
    Returns:
        Set of normalized unique skills
    """
    normalized_skills = set()
    skill_lower_map = {}
    
    # First pass: create mapping of lowercase to original
    for skill in skills:
        normalized = normalize_skill_name(skill)
        if normalized not in skill_lower_map:
            skill_lower_map[normalized] = skill
        else:
            # If duplicate found, keep the shorter/more standard version
            existing = skill_lower_map[normalized]
            if len(skill) < len(existing) or (skill.lower() == skill and existing.lower() != existing):
                skill_lower_map[normalized] = skill
    
    # Second pass: remove base skill if full name exists
    # (e.g., if both "Excel" and "MS Excel" exist, keep "MS Excel")
    final_skills = set()
    skill_list = list(skill_lower_map.values())
    
    for skill in skill_list:
        normalized = normalize_skill_name(skill)
        # Check if this is a base of another skill
        is_base = False
        for other_skill in skill_list:
            if skill != other_skill:
                other_normalized = normalize_skill_name(other_skill)
                if normalized in other_normalized and len(normalized) < len(other_normalized):
                    is_base = True
                    break
        if not is_base:
            final_skills.add(skill)
    
    return final_skills if final_skills else set(skill_lower_map.values())


def get_skills_by_category(skills: Set[str], skill_dict: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Group extracted skills by category.
    
    Args:
        skills: Set of extracted skills
        skill_dict: Skill dictionary with categories
        
    Returns:
        Dictionary mapping categories to skill lists
    """
    categorized = {}
    
    for category, category_skills in skill_dict.items():
        category_matches = [s for s in skills if s in category_skills]
        if category_matches:
            categorized[category] = category_matches
    
    return categorized

