"""
Resume Skills Gap Analyzer - Streamlit Application
Main application file for analyzing resume skills gaps and providing prescriptive optimization.
"""

import streamlit as st
import os
import sys
from typing import Set, List, Dict
import pandas as pd

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
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

# --- Page configuration ---
st.set_page_config(
    page_title="Resume Skills Gap Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
.main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4; text-align: center; margin-bottom: 0.5rem; }
.sub-header { font-size: 1.2rem; color: #666; text-align: center; margin-bottom: 2rem; }
.match-score { font-size: 3rem; font-weight: bold; text-align: center; padding: 1rem; }
.skill-badge { display: inline-block; padding: 0.3rem 0.8rem; margin: 0.2rem; background-color: #e3f2fd; border-radius: 15px; font-size: 0.9rem; }
.priority-high { color: #d32f2f; font-weight: bold; }
.priority-medium { color: #f57c00; font-weight: bold; }
.priority-low { color: #757575; }
</style>
""", unsafe_allow_html=True)

# --- Data loading ---
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

# --- Display results ---
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
        if missing_skills.get('HIGH'):
            st.markdown('<p class="priority-high">🔴 High Priority (Required Skills)</p>', unsafe_allow_html=True)
            for skill in missing_skills['HIGH']:
                st.write(f"• {skill}")
            st.markdown("<br>", unsafe_allow_html=True)
        if missing_skills.get('MEDIUM'):
            st.markdown('<p class="priority-medium">🟠 Medium Priority (Preferred Skills)</p>', unsafe_allow_html=True)
            for skill in missing_skills['MEDIUM']:
                st.write(f"• {skill}")
            st.markdown("<br>", unsafe_allow_html=True)
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
                }[priority]
                with st.expander(priority_label, expanded=(priority == 'HIGH')):
                    for rec in recommendations[priority]:
                        skill_name = rec.get('skill', 'Unknown')
                        timeline = rec.get('timeline', 'N/A')
                        st.markdown(f"### {skill_name}")
                        st.write(f"**Estimated Learning Time:** {timeline}")
                        resources = rec.get('resources', [])
                        if resources:
                            st.write("**Learning Resources:**")
                            for res in resources:
                                platform = res.get('platform', 'Unknown')
                                course = res.get('course', 'Unknown')
                                url = res.get('url', '#')
                                st.markdown(f"- **{platform}:** [{course}]({url})")
                        resume_bullet = rec.get('resume_bullet', '')
                        if resume_bullet:
                            st.write("**Resume Improvement Suggestion:**")
                            st.info(resume_bullet)
                        st.markdown("---")
    else:
        st.info("No recommendations available. Great job on having all the skills!")

# --- Main application ---
def main():
    st.markdown('<div class="main-header">📊 Resume Skills Gap Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload resume → Paste job description → Identify skill gaps</div>', unsafe_allow_html=True)

    # Load data
    skill_dict, job_templates = load_data()
    if skill_dict is None or job_templates is None:
        st.error("Failed to load required data files. Ensure data/skill_dictionary.json and data/job_role_templates.json exist.")
        return

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        selected_template = st.selectbox("Select Job Template (Optional)", options=["None"] + list(job_templates.keys()))
        if selected_template != "None":
            template_data = job_templates[selected_template]
            st.info(f"Template: {selected_template}")
            st.write("**Required:**", ", ".join(template_data.get("required", [])))
            st.write("**Preferred:**", ", ".join(template_data.get("preferred", [])))

    # Main content
    col1, col2 = st.columns([1,1])
    with col1:
        st.subheader("📄 Upload Resume")
        uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt'])
        if uploaded_file:
            st.success(f"File uploaded: {uploaded_file.name}")
            file_type = uploaded_file.name.split('.')[-1]
    with col2:
        st.subheader("💼 Job Description")
        job_description = st.text_area("Paste job description here", height=200)
        if selected_template != "None" and not job_description:
            template_data = job_templates[selected_template]
            template_text = f"Required Skills: {', '.join(template_data.get('required', []))}\n\n"
            template_text += f"Preferred Skills: {', '.join(template_data.get('preferred', []))}\n\n"
            template_text += f"Bonus Skills: {', '.join(template_data.get('bonus', []))}"
            job_description = st.text_area("Paste job description here", value=template_text, height=200)

    # Analyze
    analyze_button = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)
    if analyze_button:
        if uploaded_file is None:
            st.error("❌ Please upload a resume file.")
            return
        if not job_description or len(job_description.strip()) < 10:
            st.error("❌ Please provide a job description.")
            return

        with st.spinner("Analyzing resume..."):
            try:
                file_bytes = uploaded_file.read()
                resume_text = extract_text_from_file(file_bytes, file_type)
                resume_skills = normalize_duplicates(extract_skills_from_text(resume_text, skill_dict))

                job_required, job_preferred, job_bonus, or_groups = extract_skills_from_job_description(
                    job_description, skill_dict, job_templates
                )

                if selected_template != "None" and len(job_required) == 0:
                    template_data = job_templates[selected_template]
                    job_required = template_data.get("required", [])
                    job_preferred = template_data.get("preferred", [])
                    job_bonus = template_data.get("bonus", [])
                    or_groups = {}

                match_score, match_details = weighted_match_score(
                    resume_skills, job_required, job_preferred, job_bonus, or_groups
                )
                missing_skills = find_missing_skills(
                    resume_skills, job_required, job_preferred, job_bonus, or_groups
                )
                recommendations = generate_recommendations(missing_skills)

                st.session_state['analysis_results'] = {
                    'match_score': match_score,
                    'resume_skills': resume_skills,
                    'job_skills': {'required': job_required, 'preferred': job_preferred, 'bonus': job_bonus},
                    'missing_skills': missing_skills,
                    'recommendations': recommendations,
                    'match_details': match_details
                }

            except Exception as e:
                st.error(f"❌ Analysis error: {e}")
                st.exception(e)
                return

        display_results(match_score, match_details, resume_skills, job_required, job_preferred, job_bonus, missing_skills, recommendations)

    elif 'analysis_results' in st.session_state:
        results = st.session_state['analysis_results']
        display_results(
            results['match_score'], results['match_details'],
            results['resume_skills'], results['job_skills']['required'],
            results['job_skills']['preferred'], results['job_skills']['bonus'],
            results['missing_skills'], results['recommendations']
        )

    # --- PDF Export ---
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
            st.error(f"Error generating PDF: {e}")
            st.exception(e)

if __name__ == "__main__":
    main()

