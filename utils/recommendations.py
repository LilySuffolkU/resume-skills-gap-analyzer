"""
Recommendation engine for learning resources and resume improvements.
Provides personalized learning plans for missing skills.
"""

from typing import Dict, List
import random


# Learning resource database
LEARNING_RESOURCES = {
    'python': [
        {'platform': 'Coursera', 'course': 'Python for Everybody', 'url': 'https://www.coursera.org/specializations/python'},
        {'platform': 'Udemy', 'course': 'Complete Python Bootcamp', 'url': 'https://www.udemy.com/course/complete-python-bootcamp/'},
        {'platform': 'YouTube', 'course': 'Python Tutorial for Beginners', 'url': 'https://www.youtube.com/results?search_query=python+tutorial'}
    ],
    'java': [
        {'platform': 'Coursera', 'course': 'Java Programming and Software Engineering', 'url': 'https://www.coursera.org/specializations/java-programming'},
        {'platform': 'Udemy', 'course': 'Java Programming Masterclass', 'url': 'https://www.udemy.com/course/java-the-complete-java-developer-course/'},
        {'platform': 'YouTube', 'course': 'Java Tutorial for Beginners', 'url': 'https://www.youtube.com/results?search_query=java+tutorial'}
    ],
    'javascript': [
        {'platform': 'Coursera', 'course': 'JavaScript for Beginners', 'url': 'https://www.coursera.org/learn/javascript-basics'},
        {'platform': 'Udemy', 'course': 'The Complete JavaScript Course', 'url': 'https://www.udemy.com/course/the-complete-javascript-course/'},
        {'platform': 'YouTube', 'course': 'JavaScript Crash Course', 'url': 'https://www.youtube.com/results?search_query=javascript+tutorial'}
    ],
    'react': [
        {'platform': 'Coursera', 'course': 'React Basics', 'url': 'https://www.coursera.org/learn/react-basics'},
        {'platform': 'Udemy', 'course': 'The Complete React Developer Course', 'url': 'https://www.udemy.com/course/react-redux/'},
        {'platform': 'YouTube', 'course': 'React Tutorial for Beginners', 'url': 'https://www.youtube.com/results?search_query=react+tutorial'}
    ],
    'sql': [
        {'platform': 'Coursera', 'course': 'SQL for Data Science', 'url': 'https://www.coursera.org/learn/sql-for-data-science'},
        {'platform': 'Udemy', 'course': 'The Complete SQL Bootcamp', 'url': 'https://www.udemy.com/course/the-complete-sql-bootcamp/'},
        {'platform': 'YouTube', 'course': 'SQL Tutorial for Beginners', 'url': 'https://www.youtube.com/results?search_query=sql+tutorial'}
    ],
    'aws': [
        {'platform': 'Coursera', 'course': 'AWS Fundamentals', 'url': 'https://www.coursera.org/specializations/aws-fundamentals'},
        {'platform': 'Udemy', 'course': 'AWS Certified Solutions Architect', 'url': 'https://www.udemy.com/course/aws-certified-solutions-architect-associate/'},
        {'platform': 'YouTube', 'course': 'AWS Tutorial for Beginners', 'url': 'https://www.youtube.com/results?search_query=aws+tutorial'}
    ],
    'docker': [
        {'platform': 'Coursera', 'course': 'Docker and Kubernetes', 'url': 'https://www.coursera.org/learn/docker-kubernetes'},
        {'platform': 'Udemy', 'course': 'Docker Mastery', 'url': 'https://www.udemy.com/course/docker-mastery/'},
        {'platform': 'YouTube', 'course': 'Docker Tutorial', 'url': 'https://www.youtube.com/results?search_query=docker+tutorial'}
    ],
    'git': [
        {'platform': 'Coursera', 'course': 'Version Control with Git', 'url': 'https://www.coursera.org/learn/version-control-with-git'},
        {'platform': 'Udemy', 'course': 'Git Complete', 'url': 'https://www.udemy.com/course/git-complete/'},
        {'platform': 'YouTube', 'course': 'Git Tutorial for Beginners', 'url': 'https://www.youtube.com/results?search_query=git+tutorial'}
    ],
    'machine learning': [
        {'platform': 'Coursera', 'course': 'Machine Learning', 'url': 'https://www.coursera.org/learn/machine-learning'},
        {'platform': 'Udemy', 'course': 'Machine Learning A-Z', 'url': 'https://www.udemy.com/course/machinelearning/'},
        {'platform': 'YouTube', 'course': 'Machine Learning Tutorial', 'url': 'https://www.youtube.com/results?search_query=machine+learning+tutorial'}
    ],
    'data analysis': [
        {'platform': 'Coursera', 'course': 'Data Analysis with Python', 'url': 'https://www.coursera.org/learn/data-analysis-with-python'},
        {'platform': 'Udemy', 'course': 'Data Analysis with Pandas', 'url': 'https://www.udemy.com/course/data-analysis-with-pandas/'},
        {'platform': 'YouTube', 'course': 'Data Analysis Tutorial', 'url': 'https://www.youtube.com/results?search_query=data+analysis+tutorial'}
    ]
}


def get_learning_timeline(skill: str, priority: str) -> str:
    """
    Estimate learning timeline for a skill based on priority.
    
    Args:
        skill: Skill name
        priority: Priority level (HIGH, MEDIUM, LOW)
        
    Returns:
        Timeline estimate (e.g., "1 week", "1 month", "3 months")
    """
    # Complex skills typically take longer
    complex_skills = ['machine learning', 'data science', 'cloud architecture', 'devops', 'full stack']
    skill_lower = skill.lower()
    
    is_complex = any(complex in skill_lower for complex in complex_skills)
    
    if priority == 'HIGH':
        return "2-4 weeks" if not is_complex else "1-2 months"
    elif priority == 'MEDIUM':
        return "1-2 weeks" if not is_complex else "3-4 weeks"
    else:
        return "1 week" if not is_complex else "2-3 weeks"


def find_resource_for_skill(skill: str) -> List[Dict]:
    """
    Find learning resources for a given skill.
    
    Args:
        skill: Skill name
        
    Returns:
        List of 1-2 learning resources
    """
    skill_lower = skill.lower()
    
    # Direct match
    if skill_lower in LEARNING_RESOURCES:
        resources = LEARNING_RESOURCES[skill_lower]
        return random.sample(resources, min(2, len(resources)))
    
    # Partial match
    for key, resources in LEARNING_RESOURCES.items():
        if key in skill_lower or skill_lower in key:
            return random.sample(resources, min(2, len(resources)))
    
    # Default generic resources
    return [
        {'platform': 'Coursera', 'course': f'{skill} Course', 'url': f'https://www.coursera.org/search?query={skill}'},
        {'platform': 'Udemy', 'course': f'Learn {skill}', 'url': f'https://www.udemy.com/courses/search/?q={skill}'}
    ]


def generate_resume_bullet(skill: str) -> str:
    """
    Generate a resume bullet point suggestion for a skill.
    
    Args:
        skill: Skill name
        
    Returns:
        Resume bullet point suggestion
    """
    skill_lower = skill.lower()
    
    # Programming languages
    if any(lang in skill_lower for lang in ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust']):
        return f"Developed applications using {skill} to improve system performance and user experience"
    
    # Frameworks
    elif any(fw in skill_lower for fw in ['react', 'angular', 'vue', 'django', 'flask', 'spring']):
        return f"Built responsive web applications using {skill} framework, enhancing user engagement"
    
    # Databases
    elif any(db in skill_lower for db in ['sql', 'mysql', 'postgresql', 'mongodb', 'redis']):
        return f"Designed and optimized database schemas using {skill}, reducing query time by 30%"
    
    # Cloud/DevOps
    elif any(cloud in skill_lower for cloud in ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd']):
        return f"Deployed scalable infrastructure using {skill}, improving system reliability and reducing costs"
    
    # Data Science
    elif any(ds in skill_lower for ds in ['machine learning', 'data analysis', 'pandas', 'numpy', 'tensorflow']):
        return f"Applied {skill} to analyze data and build predictive models, driving data-driven decisions"
    
    # General
    else:
        return f"Utilized {skill} to streamline processes and enhance project outcomes"


def generate_recommendations(missing_skills: Dict[str, List[str]]) -> Dict[str, List[Dict]]:
    """
    Generate comprehensive recommendations for missing skills.
    
    Args:
        missing_skills: Dictionary with HIGH, MEDIUM, LOW priority skills
        
    Returns:
        Dictionary mapping priorities to recommendation lists
        Each recommendation contains: skill, resources, timeline, resume_bullet
    """
    recommendations = {
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }
    
    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        for skill in missing_skills.get(priority, []):
            resources = find_resource_for_skill(skill)
            timeline = get_learning_timeline(skill, priority)
            resume_bullet = generate_resume_bullet(skill)
            
            recommendations[priority].append({
                'skill': skill,
                'resources': resources[:2],  # Limit to 2 resources
                'timeline': timeline,
                'resume_bullet': resume_bullet
            })
    
    return recommendations

