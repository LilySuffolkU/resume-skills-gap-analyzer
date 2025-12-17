"""
Resume Skills Gap Analyzer - Streamlit Application
Main application file for analyzing resume skills gaps.
"""

import streamlit as st
import os
import json
from typing import Set, List, Dict
import sys
import pandas as pd

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.text_extraction import extract_text_from_file
from utils.skill_extraction import load_skill_dictionary, extract_skills_from_text, normalize_duplicates
from utils.gap_analysis import (
    load_job_role_templates,
    weighted_match_score,
    find_missing_skills,
    extract_skills_from_job_description
)
from utils.recommendations import generate_recommendations
from utils.pdf_export import create_pdf_report
from utils.optimization import optimize_skill_learning, calculate_expected_score_improvement


# Page configuration
st.set_page_config(
    page_title="Resume Skills Gap Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .match-score {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
    }
    .skill-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        background-color: #e3f2fd;
        border-radius: 15px;
        font-size: 0.9rem;
    }
    .priority-high {
        color: #d32f2f;
        font-weight: bold;
    }
    .priority-medium {
        color: #f57c00;
        font-weight: bold;
    }
    .priority-low {
        color: #757575;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load skill dictionary and job templates (cached)."""
    try:
        skill_dict = load_skill_dictionary("data/skill_dictionary.json")
        job_templates = load_job_role_templates("data/job_role_templates.json")
        return skill_dict, job_templates
    except Exception as e:
        st.error(f"Error loading data files: {str(e)}")
        return None, None


def main():
    """Main application function."""
    
    # Header
    st.markdown('<div class="main-header">📊 Resume Skills Gap Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload resume → Paste job description → Identify skill gaps</div>', unsafe_allow_html=True)
    
    # Load data
    skill_dict, job_templates = load_data()
    if skill_dict is None or job_templates is None:
        st.error("Failed to load required data files. Please ensure data/skill_dictionary.json and data/job_role_templates.json exist.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        selected_template = st.selectbox(
            "Select Job Template (Optional)",
            options=["None"] + list(job_templates.keys()),
            help="Pre-fill job description with a template"
        )
        
        if selected_template != "None":
            template_data = job_templates[selected_template]
            st.info(f"Template: {selected_template}")
            st.write("**Required:**", ", ".join(template_data.get("required", [])))
            st.write("**Preferred:**", ", ".join(template_data.get("preferred", [])))
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT"
        )
        
        if uploaded_file is not None:
            st.success(f"File uploaded: {uploaded_file.name}")
            file_type = uploaded_file.name.split('.')[-1]
    
    with col2:
        st.subheader("💼 Job Description")
        job_description = st.text_area(
            "Paste job description here",
            height=200,
            help="Paste the complete job description including required and preferred skills"
        )
        
        # Pre-fill with template if selected
        if selected_template != "None" and not job_description:
            template_data = job_templates[selected_template]
            template_text = f"Required Skills: {', '.join(template_data.get('required', []))}\n\n"
            template_text += f"Preferred Skills: {', '.join(template_data.get('preferred', []))}\n\n"
            template_text += f"Bonus Skills: {', '.join(template_data.get('bonus', []))}"
            job_description = st.text_area(
                "Paste job description here",
                value=template_text,
                height=200
            )
    
    # Analyze button
    analyze_button = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)
    
    # Analysis results
    if analyze_button:
        # Validation
        if uploaded_file is None:
            st.error("❌ Please upload a resume file.")
            return
        
        if not job_description or len(job_description.strip()) < 10:
            st.error("❌ Please provide a job description (at least 10 characters).")
            return
        
        # Show progress
        with st.spinner("Analyzing resume and extracting skills..."):
            try:
                # Extract text from resume
                file_bytes = uploaded_file.read()
                resume_text = extract_text_from_file(file_bytes, file_type)
                
                if not resume_text or len(resume_text.strip()) < 10:
                    st.error("❌ Failed to extract text from resume. The file may be corrupted or empty.")
                    return
                
                # Extract skills from resume
                resume_skills = extract_skills_from_text(resume_text, skill_dict)
                resume_skills = normalize_duplicates(resume_skills)
                
                if not resume_skills:
                    st.warning("⚠️ No skills detected in resume. Please ensure your resume contains technical skills.")
                    return
                
                # Extract skills from job description
                job_required, job_preferred, job_bonus, or_groups = extract_skills_from_job_description(
                    job_description, skill_dict, job_templates
                )
                
                # Use template if provided and job description is minimal
                if selected_template != "None" and len(job_required) == 0:
                    template_data = job_templates[selected_template]
                    job_required = template_data.get("required", [])
                    job_preferred = template_data.get("preferred", [])
                    job_bonus = template_data.get("bonus", [])
                    or_groups = {}  # Templates don't have "or" groups
                
                # Compute match score
                match_score, match_details = weighted_match_score(
                    resume_skills,
                    job_required,
                    job_preferred,
                    job_bonus,
                    or_groups
                )
                
                # Find missing skills
                missing_skills = find_missing_skills(
                    resume_skills,
                    job_required,
                    job_preferred,
                    job_bonus,
                    or_groups
                )
                
                # Generate recommendations
                recommendations = generate_recommendations(missing_skills)
                
                # Store in session state for PDF export
                st.session_state['analysis_results'] = {
                    'match_score': match_score,
                    'resume_skills': resume_skills,
                    'job_skills': {
                        'required': job_required,
                        'preferred': job_preferred,
                        'bonus': job_bonus
                    },
                    'missing_skills': missing_skills,
                    'recommendations': recommendations,
                    'match_details': match_details
                }
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.exception(e)
                return
        
        # Display results
        display_results(
            match_score,
            match_details,
            resume_skills,
            job_required,
            job_preferred,
            job_bonus,
            missing_skills,
            recommendations
        )
    
    # Display results from session state if available
    elif 'analysis_results' in st.session_state:
        results = st.session_state['analysis_results']
        display_results(
            results['match_score'],
            results['match_details'],
            results['resume_skills'],
            results['job_skills']['required'],
            results['job_skills']['preferred'],
            results['job_skills']['bonus'],
            results['missing_skills'],
            results['recommendations']
        )


def display_results(
    match_score: float,
    match_details: Dict,
    resume_skills: Set[str],
    job_required: List[str],
    job_preferred: List[str],
    job_bonus: List[str],
    missing_skills: Dict[str, List[str]],
    recommendations: Dict[str, List[Dict]]
):
    """Display analysis results in the UI."""
    
    st.markdown("---")
    st.header("📊 Analysis Results")
    
    # Match Score
    score_percent = match_score * 100
    score_color = "#d32f2f" if score_percent < 50 else "#f57c00" if score_percent < 75 else "#388e3c"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<div class="match-score" style="color: {score_color}">{score_percent:.1f}% Match</div>', unsafe_allow_html=True)
        
        # Match details
        if match_details:
            st.write(f"**Required Skills:** {match_details.get('required_match', 0)}/{match_details.get('required_total', 0)} matched")
            st.write(f"**Preferred Skills:** {match_details.get('preferred_match', 0)}/{match_details.get('preferred_total', 0)} matched")
            st.write(f"**Bonus Skills:** {match_details.get('bonus_match', 0)}/{match_details.get('bonus_total', 0)} matched")
    
    st.markdown("---")
    
    # Skills comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Resume Skills")
        if resume_skills:
            skills_html = " ".join([f'<span class="skill-badge">{skill}</span>' for skill in sorted(resume_skills)])
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.write("No skills detected.")
    
    with col2:
        st.subheader("🎯 Job Requirements")
        if job_required:
            st.write("**Required:**")
            req_html = " ".join([f'<span class="skill-badge" style="background-color: #ffebee;">{skill}</span>' for skill in job_required])
            st.markdown(req_html, unsafe_allow_html=True)
        
        if job_preferred:
            st.write("**Preferred:**")
            pref_html = " ".join([f'<span class="skill-badge" style="background-color: #fff3e0;">{skill}</span>' for skill in job_preferred])
            st.markdown(pref_html, unsafe_allow_html=True)
        
        if job_bonus:
            st.write("**Bonus:**")
            bonus_html = " ".join([f'<span class="skill-badge" style="background-color: #f5f5f5;">{skill}</span>' for skill in job_bonus])
            st.markdown(bonus_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Missing Skills
    st.subheader("⚠️ Missing Skills")
    
    total_missing = sum(len(skills) for skills in missing_skills.values())
    if total_missing == 0:
        st.success("🎉 Congratulations! You have all the required skills!")
    else:
        # High Priority
        if missing_skills.get('HIGH'):
            st.markdown('<p class="priority-high">🔴 High Priority (Required Skills)</p>', unsafe_allow_html=True)
            for skill in missing_skills['HIGH']:
                st.write(f"• {skill}")
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Medium Priority
        if missing_skills.get('MEDIUM'):
            st.markdown('<p class="priority-medium">🟠 Medium Priority (Preferred Skills)</p>', unsafe_allow_html=True)
            for skill in missing_skills['MEDIUM']:
                st.write(f"• {skill}")
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Low Priority
        if missing_skills.get('LOW'):
            st.markdown('<p class="priority-low">⚪ Low Priority (Bonus Skills)</p>', unsafe_allow_html=True)
            for skill in missing_skills['LOW']:
                st.write(f"• {skill}")
    
    st.markdown("---")
    
    # Recommendations
    st.subheader("📚 Learning Recommendations")
    
    has_recommendations = any(recommendations.get(priority) for priority in ['HIGH', 'MEDIUM', 'LOW'])
    
    if has_recommendations:
        for priority in ['HIGH', 'MEDIUM', 'LOW']:
            if recommendations.get(priority):
                priority_label = {
                    'HIGH': '🔴 High Priority Skills',
                    'MEDIUM': '🟠 Medium Priority Skills',
                    'LOW': '⚪ Low Priority Skills'
                }.get(priority, priority)
                
                with st.expander(priority_label, expanded=(priority == 'HIGH')):
                    for rec in recommendations[priority]:
                        skill_name = rec.get('skill', 'Unknown')
                        timeline = rec.get('timeline', 'N/A')
                        
                        st.markdown(f"### {skill_name}")
                        st.write(f"**Estimated Learning Time:** {timeline}")
                        
                        # Resources
                        resources = rec.get('resources', [])
                        if resources:
                            st.write("**Learning Resources:**")
                            for resource in resources:
                                platform = resource.get('platform', 'Unknown')
                                course = resource.get('course', 'Unknown')
                                url = resource.get('url', '#')
                                st.markdown(f"- **{platform}:** [{course}]({url})")
                        
                        # Resume bullet
                        resume_bullet = rec.get('resume_bullet', '')
                        if resume_bullet:
                            st.write("**Resume Improvement Suggestion:**")
                            st.info(resume_bullet)
                        
                        st.markdown("---")
    else:
        st.info("No recommendations available. Great job on having all the skills!")
    
    st.markdown("---")
    
    # Prescriptive Optimization Section
    st.markdown("## 🎯 Prescriptive Optimization: Optimal Skill Learning Plan")
    st.markdown(
        """
        <div style="background-color: #e3f2fd; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
        <strong>What is Prescriptive Analytics?</strong><br>
        This optimization engine uses <strong>integer linear programming (PuLP)</strong> to find the <strong>optimal sequence of skills to learn</strong> 
        that maximizes your job match score improvement within your time and budget constraints. 
        Unlike recommendations (which suggest what to learn), this provides an <strong>optimized solution</strong> 
        that answers: "Given X months and $Y budget, which skills should I learn to maximize my match score?"
        </div>
        """,
        unsafe_allow_html=True
    )
    
    total_missing = sum(len(skills) for skills in missing_skills.values())
    if total_missing > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            time_budget = st.number_input(
                "⏱️ Time Budget (months)",
                min_value=0.1,
                max_value=24.0,
                value=3.0,
                step=0.5,
                help="Maximum time available for learning (e.g., 3 months)"
            )
        
        with col2:
            cost_budget = st.number_input(
                "💰 Budget ($)",
                min_value=0.0,
                max_value=10000.0,
                value=500.0,
                step=50.0,
                help="Maximum budget for courses and learning resources"
            )
        
        optimize_button = st.button("🔬 Optimize Learning Plan", type="primary", use_container_width=True)
        
        if not optimize_button:
            st.info("💡 Click the button above to find the optimal skill learning plan that maximizes your match score within your constraints.")
        
        if optimize_button:
            with st.spinner("Solving optimization problem..."):
                try:
                    # Run optimization
                    selected_skills, skill_details, objective_value, status = optimize_skill_learning(
                        missing_skills,
                        time_budget,
                        cost_budget
                    )
                    
                    # Calculate expected score improvement
                    if 'analysis_results' in st.session_state:
                        results = st.session_state['analysis_results']
                        score_improvement = calculate_expected_score_improvement(
                            selected_skills,
                            results['match_details'],
                            job_required,
                            job_preferred,
                            job_bonus
                        )
                    else:
                        score_improvement = {
                            'current_score': match_score,
                            'expected_score': match_score + objective_value / 10,  # Rough estimate
                            'score_improvement': objective_value / 10
                        }
                    
                    # Display optimization results
                    st.success("✅ Optimization Complete!")
                    st.info(status)
                    
                    st.markdown("---")
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    total_selected = sum(len(skills) for skills in selected_skills.values())
                    total_time = sum(details['time_months'] for details in skill_details.values())
                    total_cost = sum(details['cost_dollars'] for details in skill_details.values())
                    
                    with col1:
                        st.metric("Skills Selected", total_selected)
                    with col2:
                        st.metric("Total Time", f"{total_time:.1f} months")
                    with col3:
                        st.metric("Total Cost", f"${total_cost:.0f}")
                    with col4:
                        st.metric(
                            "Score Improvement", 
                            f"+{score_improvement['score_improvement']*100:.1f}%",
                            delta=f"{score_improvement['current_score']*100:.1f}% → {score_improvement['expected_score']*100:.1f}%"
                        )
                    
                    st.markdown("---")
                    
                    # Optimal skill learning plan
                    st.subheader("📋 Optimal Learning Plan")
                    
                    if total_selected > 0:
                        # Sort skills by priority and display
                        for priority in ['HIGH', 'MEDIUM', 'LOW']:
                            if selected_skills.get(priority):
                                priority_label = {
                                    'HIGH': '🔴 High Priority (Required Skills)',
                                    'MEDIUM': '🟠 Medium Priority (Preferred Skills)',
                                    'LOW': '⚪ Low Priority (Bonus Skills)'
                                }.get(priority, priority)
                                
                                st.markdown(f"### {priority_label}")
                                
                                # Create a table for selected skills
                                import pandas as pd
                                skill_data = []
                                for skill in selected_skills[priority]:
                                    details = skill_details[skill]
                                    skill_data.append({
                                        'Skill': skill,
                                        'Time (months)': f"{details['time_months']:.2f}",
                                        'Cost ($)': f"{details['cost_dollars']:.0f}",
                                        'Score Weight': f"{details['score_weight']:.2f}"
                                    })
                                
                                if skill_data:
                                    df = pd.DataFrame(skill_data)
                                    st.dataframe(df, use_container_width=True, hide_index=True)
                                
                                st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Learning sequence recommendation
                        st.markdown("### 📅 Recommended Learning Sequence")
                        st.info(
                            "Learn skills in priority order (HIGH → MEDIUM → LOW) for maximum impact. " 
                            "You can learn multiple skills in parallel if time permits."
                        )
                        
                        # Show unused budget
                        unused_time = time_budget - total_time
                        unused_cost = cost_budget - total_cost
                        
                        if unused_time > 0.1 or unused_cost > 10:
                            st.markdown("### 💡 Budget Utilization")
                            col1, col2 = st.columns(2)
                            with col1:
                                time_pct = (total_time / time_budget * 100) if time_budget > 0 else 0
                                st.metric("Time Used", f"{time_pct:.1f}%", f"{unused_time:.1f} months remaining")
                            with col2:
                                cost_pct = (total_cost / cost_budget * 100) if cost_budget > 0 else 0
                                st.metric("Budget Used", f"{cost_pct:.1f}%", f"${unused_cost:.0f} remaining")
                    else:
                        st.warning(
                            "⚠️ No skills could be selected within the given constraints. " 
                            "Try increasing your time budget or cost budget."
                        )
                    
                    # Store optimization results
                    st.session_state['optimization_results'] = {
                        'selected_skills': selected_skills,
                        'skill_details': skill_details,
                        'objective_value': objective_value,
                        'status': status,
                        'score_improvement': score_improvement,
                        'time_budget': time_budget,
                        'cost_budget': cost_budget
                    }
                    
                except ImportError as e:
                    st.error(f"❌ Optimization library not available: {str(e)}")
                    st.info("Please install PuLP or scipy: `pip install pulp` or `pip install scipy`")
                except Exception as e:
                    st.error(f"❌ Error during optimization: {str(e)}")
                    st.exception(e)
    else:
        st.info("🎉 No missing skills to optimize! You're already well-matched for this position.")
    
    st.markdown("---")
    
    # PDF Export
    st.subheader("📥 Export Report")
    
    if 'analysis_results' in st.session_state:
        results = st.session_state['analysis_results']
        
        try:
            pdf_buffer = create_pdf_report(
                results['match_score'],
                results['resume_skills'],
                results['job_skills'],
                results['missing_skills'],
                results['recommendations'],
                results['match_details']
            )
            
            st.download_button(
                label="📄 Download Report as PDF",
                data=pdf_buffer,
                file_name="resume_skills_gap_analysis.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            st.exception(e)


if __name__ == "__main__":
    main()
