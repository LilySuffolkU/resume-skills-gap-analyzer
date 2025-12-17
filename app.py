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
    
    # ============================================================================
    # PRESCRIPTIVE OPTIMIZATION MODEL - PRIMARY COMPONENT
    # ============================================================================
    st.markdown("## 🎯 Prescriptive Optimization Model")
    
    st.markdown(
        """
        <div style="background-color: #fff3cd; padding: 1rem; border-left: 4px solid #ffc107; margin-bottom: 1rem;">
        <strong>Prescriptive Analytics:</strong> This section uses <strong>Integer Linear Programming (ILP)</strong> 
        to determine the <strong>optimal decision</strong> of which skills to learn, maximizing your job match score 
        improvement subject to time and budget constraints.
        </div>
        """,
        unsafe_allow_html=True
    )
    # Mathematical Formulation
    with st.expander("📐 Optimization Model Formulation", expanded=True):
        st.markdown("### Decision Variables")
        st.latex(r"x_i \in \{0, 1\} \quad \forall i \in \text{missing skills}")
        st.markdown("*Binary variable: $x_i = 1$ if skill $i$ is selected for learning, $x_i = 0$ otherwise*")
        
        st.markdown("### Objective Function")
        st.latex(r"\max \sum_{i} w_i \cdot x_i")
        st.markdown("*Maximize weighted job match score improvement, where $w_i$ is the score weight for skill $i$*")
        
        st.markdown("### Constraints")
        st.latex(r"\sum_{i} t_i \cdot x_i \leq T")
        st.markdown("*Total learning time must not exceed time budget $T$ (months)*")
        
        st.latex(r"\sum_{i} c_i \cdot x_i \leq C")
        st.markdown("*Total learning cost must not exceed cost budget $C$ (dollars)*")
        
        st.latex(r"x_i \in \{0, 1\} \quad \forall i")
        st.markdown("*Binary decision variables*")
        
        st.markdown("---")
        st.markdown("**Where:**")
        st.markdown("- $w_i$ = score weight for skill $i$ (required: 1.0, preferred: 0.6, bonus: 0.3)")
        st.markdown("- $t_i$ = estimated learning time for skill $i$ (months)")
        st.markdown("- $c_i$ = estimated learning cost for skill $i$ (dollars)")
        st.markdown("- $T$ = user-specified time budget (months)")
        st.markdown("- $C$ = user-specified cost budget (dollars)")
    
    total_missing = sum(len(skills) for skills in missing_skills.values())
    if total_missing > 0:
        st.markdown("### Optimization Inputs")
        
        # Constraint inputs
        col1, col2 = st.columns(2)
        
        with col1:
            time_budget = st.number_input(
                "⏱️ Time Budget, $T$ (months)",
                min_value=0.1,
                max_value=24.0,
                value=3.0,
                step=0.5,
                help="Maximum time available for learning (constraint: Σ tᵢ xᵢ ≤ T)"
            )
        
        with col2:
            cost_budget = st.number_input(
                "💰 Cost Budget, $C$ ($)",
                min_value=0.0,
                max_value=10000.0,
                value=500.0,
                step=50.0,
                help="Maximum budget for courses and learning resources (constraint: Σ cᵢ xᵢ ≤ C)"
            )
        
        # Weight inputs (explicit)
        st.markdown("### Score Weights (Objective Function Coefficients)")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            weight_required = st.number_input(
                "Required Skill Weight, $w_{req}$",
                min_value=0.1,
                max_value=10.0,
                value=1.0,
                step=0.1,
                help="Weight for required skills in objective function"
            )
        
        with col2:
            weight_preferred = st.number_input(
                "Preferred Skill Weight, $w_{pref}$",
                min_value=0.1,
                max_value=10.0,
                value=0.6,
                step=0.1,
                help="Weight for preferred skills in objective function"
            )
        
        with col3:
            weight_bonus = st.number_input(
                "Bonus Skill Weight, $w_{bonus}$",
                min_value=0.1,
                max_value=10.0,
                value=0.3,
                step=0.1,
                help="Weight for bonus skills in objective function"
            )
        
        # Normalize weights (store in session state for optimization function)
        total_weight = weight_required + weight_preferred + weight_bonus
        if total_weight > 0:
            weight_required_norm = weight_required / total_weight
            weight_preferred_norm = weight_preferred / total_weight
            weight_bonus_norm = weight_bonus / total_weight
        else:
            weight_required_norm = 1.0
            weight_preferred_norm = 0.6
            weight_bonus_norm = 0.3
        
        st.info(f"Normalized weights: Required={weight_required_norm:.3f}, Preferred={weight_preferred_norm:.3f}, Bonus={weight_bonus_norm:.3f}")
        
        optimize_button = st.button("🔬 Solve Optimization Problem", type="primary", use_container_width=True)
        
        if not optimize_button:
            st.info("💡 Click the button above to solve the optimization problem and obtain the optimal decision.")
        
        if optimize_button:
            with st.spinner("Solving optimization problem..."):
                try:
                    # Run optimization with custom weights
                    selected_skills, skill_details, objective_value, status = optimize_skill_learning(
                        missing_skills,
                        time_budget,
                        cost_budget,
                        weight_required_norm,
                        weight_preferred_norm,
                        weight_bonus_norm
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
                    st.markdown("### Optimization Results")
                    
                    # Solver status - extract and display clearly
                    is_optimal = "Optimal" in status or "optimal" in status.lower() or "Success" in status
                    solver_status_text = status.split(":")[-1].strip() if ":" in status else status
                    
                    if is_optimal:
                        st.success("✅ **Solver Status: OPTIMAL**")
                        st.info("**This solution is optimal under the specified constraints.** The optimization model has found the best possible combination of skills to learn that maximizes your job match score improvement.")
                    else:
                        if "Infeasible" in status or "infeasible" in status.lower():
                            st.error(f"❌ **Solver Status: INFEASIBLE**")
                            st.warning("No feasible solution exists. Try relaxing your time or cost constraints.")
                        else:
                            st.warning(f"⚠️ **Solver Status:** {solver_status_text}")
                    
                    st.markdown("---")
                    
                    # Summary metrics
                    total_selected = sum(len(skills) for skills in selected_skills.values())
                    total_time = sum(details['time_months'] for details in skill_details.values())
                    total_cost = sum(details['cost_dollars'] for details in skill_details.values())
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Objective Value", f"{objective_value:.3f}", 
                                 help="Maximum weighted score improvement achieved")
                    with col2:
                        st.metric("Skills Selected", total_selected)
                    with col3:
                        time_pct = (total_time / time_budget * 100) if time_budget > 0 else 0
                        st.metric("Time Used", f"{total_time:.2f} / {time_budget:.1f} months", 
                                 f"{time_pct:.1f}%", delta_color="normal")
                    with col4:
                        cost_pct = (total_cost / cost_budget * 100) if cost_budget > 0 else 0
                        st.metric("Cost Used", f"${total_cost:.0f} / ${cost_budget:.0f}", 
                                 f"{cost_pct:.1f}%", delta_color="normal")
                    
                    # Visual confirmation: Bar chart
                    if total_selected > 0:
                        st.markdown("---")
                        st.markdown("### 📊 Budget Utilization Visualization")
                        chart_data = pd.DataFrame({
                            'Resource': ['Time Budget', 'Cost Budget'],
                            'Used (%)': [
                                (total_time / time_budget * 100) if time_budget > 0 else 0,
                                (total_cost / cost_budget * 100) if cost_budget > 0 else 0
                            ]
                        })
                        st.bar_chart(chart_data.set_index('Resource'), use_container_width=True)
                    
                    st.markdown("---")
                    
                    # Optimal Solution Table
                    st.markdown("### 📋 Optimal Solution")
                    st.markdown(
                        """
                        <div style="background-color: #d4edda; padding: 0.75rem; border-left: 4px solid #28a745; margin-bottom: 1rem;">
                        <strong>Optimal Decision:</strong> The following skills have been selected by the optimization model 
                        to maximize your job match score improvement within your constraints.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    if total_selected > 0:
                        # Create comprehensive optimal solution table
                        all_skill_data = []
                        for priority in ['HIGH', 'MEDIUM', 'LOW']:
                            for skill in selected_skills.get(priority, []):
                                details = skill_details[skill]
                                all_skill_data.append({
                                    'Priority': priority,
                                    'Skill': skill,
                                    'Time (months)': details['time_months'],
                                    'Cost ($)': details['cost_dollars'],
                                    'Score Weight': details['score_weight']
                                })
                        
                        if all_skill_data:
                            df_optimal = pd.DataFrame(all_skill_data)
                            df_optimal['Priority'] = df_optimal['Priority'].map({
                                'HIGH': '🔴 Required',
                                'MEDIUM': '🟠 Preferred', 
                                'LOW': '⚪ Bonus'
                            })
                            df_optimal = df_optimal.sort_values(['Priority', 'Score Weight'], ascending=[True, False])
                            st.dataframe(df_optimal, use_container_width=True, hide_index=True)
                            
                            # Summary statistics
                            st.markdown("**Summary:**")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(f"**Total Skills:** {len(all_skill_data)}")
                            with col2:
                                st.write(f"**Total Time:** {total_time:.2f} months")
                            with col3:
                                st.write(f"**Total Cost:** ${total_cost:.0f}")
                            
                            # Expected score improvement
                            st.markdown("---")
                            st.markdown("### Expected Match Score Improvement")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Current Score", f"{score_improvement['current_score']*100:.1f}%")
                            with col2:
                                st.metric("Expected Score", f"{score_improvement['expected_score']*100:.1f}%")
                            with col3:
                                st.metric("Improvement", f"+{score_improvement['score_improvement']*100:.1f}%",
                                         delta=f"{score_improvement['score_improvement']*100:.2f} percentage points")
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
    
    # ============================================================================
    # LEARNING RESOURCES (SECONDARY - OPTIONAL INSIGHTS)
    # ============================================================================
    st.markdown("## 📚 Learning Resources & Insights (Optional)")
    st.markdown(
        """
        <div style="background-color: #f8f9fa; padding: 1rem; border-left: 4px solid #6c757d; margin-bottom: 1rem;">
        <strong>Note:</strong> The optimization model above provides the <strong>optimal decision</strong>. 
        The resources below are <strong>optional supplementary insights</strong> to help you learn the selected skills.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    has_recommendations = any(recommendations.get(priority) for priority in ['HIGH', 'MEDIUM', 'LOW'])
    
    if has_recommendations:
        for priority in ['HIGH', 'MEDIUM', 'LOW']:
            if recommendations.get(priority):
                priority_label = {
                    'HIGH': '🔴 Required Skills',
                    'MEDIUM': '🟠 Preferred Skills',
                    'LOW': '⚪ Bonus Skills'
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
        st.info("No learning resources available. Great job on having all the skills!")
    
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

