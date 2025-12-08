"""
PDF export utility using ReportLab.
Generates comprehensive gap analysis reports.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from typing import Dict, List, Set
from datetime import datetime


def create_pdf_report(
    match_score: float,
    resume_skills: Set[str],
    job_skills: Dict[str, List[str]],
    missing_skills: Dict[str, List[str]],
    recommendations: Dict[str, List[Dict]],
    match_details: Dict = None
) -> BytesIO:
    """
    Create a PDF report with gap analysis results.
    
    Args:
        match_score: Overall match score (0-1)
        resume_skills: Set of skills found in resume
        job_skills: Dictionary with required/preferred/bonus job skills
        missing_skills: Dictionary with missing skills by priority
        recommendations: Dictionary with recommendations by priority
        match_details: Optional detailed match statistics
        
    Returns:
        BytesIO object containing PDF data
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#1f77b4'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=HexColor('#333333'),
        spaceAfter=8,
        spaceBefore=8
    )
    
    normal_style = styles['Normal']
    
    # Title
    elements.append(Paragraph("Resume Skills Gap Analysis Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Date
    date_str = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"Generated on: {date_str}", normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Match Score Section
    elements.append(Paragraph("Match Score", heading_style))
    score_percent = match_score * 100
    score_color = HexColor('#d32f2f') if score_percent < 50 else HexColor('#f57c00') if score_percent < 75 else HexColor('#388e3c')
    
    score_style = ParagraphStyle(
        'ScoreStyle',
        parent=styles['Heading1'],
        fontSize=48,
        textColor=score_color,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    elements.append(Paragraph(f"{score_percent:.1f}%", score_style))
    
    if match_details:
        details_text = f"Required Skills: {match_details.get('required_match', 0)}/{match_details.get('required_total', 0)}<br/>"
        details_text += f"Preferred Skills: {match_details.get('preferred_match', 0)}/{match_details.get('preferred_total', 0)}<br/>"
        details_text += f"Bonus Skills: {match_details.get('bonus_match', 0)}/{match_details.get('bonus_total', 0)}"
        elements.append(Paragraph(details_text, normal_style))
    
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())
    
    # Resume Skills Section
    elements.append(Paragraph("Resume Skills", heading_style))
    if resume_skills:
        skills_text = ", ".join(sorted(resume_skills))
        elements.append(Paragraph(skills_text, normal_style))
    else:
        elements.append(Paragraph("No skills detected in resume.", normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Job Requirements Section
    elements.append(Paragraph("Job Requirements", heading_style))
    
    if job_skills.get('required'):
        elements.append(Paragraph("Required Skills:", subheading_style))
        req_text = ", ".join(job_skills['required'])
        elements.append(Paragraph(req_text, normal_style))
        elements.append(Spacer(1, 0.1*inch))
    
    if job_skills.get('preferred'):
        elements.append(Paragraph("Preferred Skills:", subheading_style))
        pref_text = ", ".join(job_skills['preferred'])
        elements.append(Paragraph(pref_text, normal_style))
        elements.append(Spacer(1, 0.1*inch))
    
    if job_skills.get('bonus'):
        elements.append(Paragraph("Bonus Skills:", subheading_style))
        bonus_text = ", ".join(job_skills['bonus'])
        elements.append(Paragraph(bonus_text, normal_style))
    
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())
    
    # Missing Skills Section
    elements.append(Paragraph("Missing Skills", heading_style))
    
    # High Priority
    if missing_skills.get('HIGH'):
        elements.append(Paragraph("High Priority (Required)", subheading_style))
        for skill in missing_skills['HIGH']:
            elements.append(Paragraph(f"• {skill}", normal_style))
        elements.append(Spacer(1, 0.1*inch))
    
    # Medium Priority
    if missing_skills.get('MEDIUM'):
        elements.append(Paragraph("Medium Priority (Preferred)", subheading_style))
        for skill in missing_skills['MEDIUM']:
            elements.append(Paragraph(f"• {skill}", normal_style))
        elements.append(Spacer(1, 0.1*inch))
    
    # Low Priority
    if missing_skills.get('LOW'):
        elements.append(Paragraph("Low Priority (Bonus)", subheading_style))
        for skill in missing_skills['LOW']:
            elements.append(Paragraph(f"• {skill}", normal_style))
    
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())
    
    # Recommendations Section
    elements.append(Paragraph("Learning Recommendations", heading_style))
    
    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        if recommendations.get(priority):
            priority_label = {
                'HIGH': 'High Priority Skills',
                'MEDIUM': 'Medium Priority Skills',
                'LOW': 'Low Priority Skills'
            }.get(priority, priority)
            
            elements.append(Paragraph(priority_label, subheading_style))
            
            for rec in recommendations[priority]:
                skill_name = rec.get('skill', 'Unknown Skill')
                elements.append(Paragraph(f"<b>{skill_name}</b>", normal_style))
                
                # Timeline
                timeline = rec.get('timeline', 'N/A')
                elements.append(Paragraph(f"Estimated Learning Time: {timeline}", normal_style))
                
                # Resources
                resources = rec.get('resources', [])
                if resources:
                    elements.append(Paragraph("Learning Resources:", normal_style))
                    for resource in resources:
                        platform = resource.get('platform', 'Unknown')
                        course = resource.get('course', 'Unknown Course')
                        elements.append(Paragraph(f"  • {platform}: {course}", normal_style))
                
                # Resume bullet
                resume_bullet = rec.get('resume_bullet', '')
                if resume_bullet:
                    elements.append(Paragraph(f"Resume Suggestion: {resume_bullet}", normal_style))
                
                elements.append(Spacer(1, 0.15*inch))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

