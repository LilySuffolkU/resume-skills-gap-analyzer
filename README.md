# Resume Skills Gap Analyzer

A comprehensive Streamlit application that analyzes resumes against job descriptions to identify skill gaps and generate personalized learning recommendations.

## 🎯 Features

- **Multi-format Resume Support**: Upload resumes in PDF, DOCX, or TXT format
- **Intelligent Skill Extraction**: Automatically extracts technical skills from resumes and job descriptions using a comprehensive skill dictionary (200+ skills)
- **Semantic Matching**: Uses SBERT embeddings for intelligent skill matching beyond simple keyword matching
- **Weighted Scoring**: Calculates match scores with weighted importance (required > preferred > bonus skills)
- **Gap Analysis**: Identifies missing skills categorized by priority:
  - 🔴 **HIGH**: Required skills
  - 🟠 **MEDIUM**: Preferred skills
  - ⚪ **LOW**: Bonus skills
- **Personalized Recommendations**: For each missing skill, provides:
  - Learning resources (Coursera, Udemy, YouTube)
  - Resume bullet point suggestions
  - Estimated learning timelines
- **PDF Export**: Generate comprehensive PDF reports with all analysis results
- **Job Template Library**: Pre-configured templates for common roles (Software Engineer, Data Scientist, DevOps, etc.)

## 📋 Requirements

- Python 3.8 or higher
- All dependencies listed in `requirements.txt`

## 🚀 Installation

### 1. Clone or Download the Project

```bash
cd "Resume Skills Gap Analyze"
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The first run will download the SBERT model (`all-MiniLM-L6-v2`), which may take a few minutes.

### 4. Download spaCy Language Model (Optional but Recommended)

```bash
python -m spacy download en_core_web_sm
```

## 🏃 Running the Application

### Local Development

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Usage Instructions

1. **Upload Resume**: Click "Browse files" and select your resume (PDF, DOCX, or TXT)
2. **Enter Job Description**: Paste the job description in the text area, or select a job template from the sidebar
3. **Analyze**: Click the "🔍 Analyze Resume" button
4. **Review Results**:
   - View your match score
   - See skills found in your resume vs. job requirements
   - Identify missing skills by priority
   - Explore learning recommendations
5. **Export**: Download a comprehensive PDF report

## 📁 Project Structure

```
resume_skills_gap_analyzer/
│── app.py                      # Main Streamlit application
│── requirements.txt            # Python dependencies
│── README.md                   # This file
│
│── utils/
│     ├── text_extraction.py    # PDF/DOCX/TXT text extraction
│     ├── skill_extraction.py   # Skill keyword matching
│     ├── gap_analysis.py       # SBERT-based gap analysis
│     ├── recommendations.py   # Learning resource recommendations
│     └── pdf_export.py         # PDF report generation
│
│── data/
│     ├── skill_dictionary.json      # 200+ skills database
│     └── job_role_templates.json   # Pre-configured job templates
│
└── assets/
      └── sample_resume.txt     # Sample resume for testing
```

## 🌐 Deployment to Streamlit Cloud

### Step 1: Push to GitHub

1. Create a new repository on GitHub
2. Push your project files to the repository

```bash
git init
git add .
git commit -m "Initial commit: Resume Skills Gap Analyzer"
git remote add origin https://github.com/yourusername/your-repo-name.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository and branch
5. Set the main file path to `app.py`
6. Click "Deploy"

**Important**: Ensure your `requirements.txt` includes all dependencies. Streamlit Cloud will automatically install them.

### Step 3: Configure (if needed)

- Add any environment variables if required
- Set Python version (3.8+ recommended)

## 🔧 Configuration

### Adding Custom Skills

Edit `data/skill_dictionary.json` to add or modify skills:

```json
{
  "Your Category": [
    "Skill 1",
    "Skill 2"
  ]
}
```

### Adding Job Templates

Edit `data/job_role_templates.json` to add new job role templates:

```json
{
  "Your Job Title": {
    "required": ["Skill 1", "Skill 2"],
    "preferred": ["Skill 3"],
    "bonus": ["Skill 4"]
  }
}
```

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: SBERT model download fails

**Solution**: The model downloads automatically on first use. If it fails:
- Check your internet connection
- Try running the app again (it will retry the download)

### Issue: PDF generation fails

**Solution**: Ensure ReportLab is installed:
```bash
pip install reportlab
```

### Issue: Text extraction fails for PDF

**Solution**: Some PDFs may be image-based or encrypted. Try:
- Converting the PDF to a text file
- Using a different PDF version
- Ensuring the PDF is not password-protected

## 📝 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add more skills to the dictionary
- Improve skill matching algorithms
- Add more learning resources
- Enhance the UI/UX

## 📧 Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

## 🎉 Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- Uses [sentence-transformers](https://www.sbert.net/) for semantic similarity
- PDF generation powered by [ReportLab](https://www.reportlab.com/)

---

**Happy Analyzing! 🚀**

