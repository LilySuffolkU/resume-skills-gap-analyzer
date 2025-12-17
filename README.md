# Resume Skills Gap Analyzer

A comprehensive Streamlit application that analyzes resumes against job descriptions to identify skill gaps, generate personalized learning recommendations, and **optimize skill learning plans using prescriptive analytics**.

## 🎥 Live Demo & Video

**🌐 Live Application:** [Your Streamlit App Link Here](https://your-app-name.streamlit.app)

**📹 Video Demonstration:** [Your Video Link Here](https://youtube.com/watch?v=your-video-id)

> **Note:** Replace the links above with your actual Streamlit Cloud deployment URL and video demonstration link.

## 🎯 Features

### Diagnostic Analytics
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

### Prescriptive Analytics (Optimization)
- **🎯 Optimal Skill Learning Plan**: Uses **Integer Linear Programming (PuLP)** to find the optimal sequence of skills to learn
- **Constraint-Based Optimization**: Maximizes job match score improvement under:
  - ⏱️ **Time constraints** (e.g., "I have 3 months")
  - 💰 **Budget constraints** (e.g., "I have $500")
- **Objective Function**: Maximizes weighted score improvement (required skills weighted 1.0, preferred 0.6, bonus 0.3)
- **Prescriptive Solution**: Answers "Given X months and $Y budget, which skills should I learn to maximize my match score?"

### Additional Features
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
5. **Optimize Learning Plan** (Prescriptive Analytics):
   - Set your time budget (e.g., 3 months)
   - Set your budget constraint (e.g., $500)
   - Click "🔬 Optimize Learning Plan"
   - View the optimal skill learning sequence that maximizes your match score improvement
6. **Export**: Download a comprehensive PDF report

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
│     ├── optimization.py      # Prescriptive optimization (PuLP/scipy)
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

## 🔬 Prescriptive Analytics Implementation

This application implements **prescriptive analytics** using optimization techniques:

- **Optimization Library**: [PuLP](https://github.com/coin-or/pulp) (Integer Linear Programming)
- **Fallback Solver**: [scipy.optimize](https://docs.scipy.org/doc/scipy/reference/optimize.html) (continuous relaxation)
- **Problem Type**: 0-1 Knapsack variant with multiple constraints
- **Objective Function**: Maximize weighted job match score improvement
- **Constraints**: 
  - Time budget (months)
  - Cost budget (dollars)
- **Decision Variables**: Binary (learn skill or not)

The optimization engine answers the prescriptive question: *"Given my constraints, what is the optimal set of skills to learn?"*

## 🎉 Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- Uses [sentence-transformers](https://www.sbert.net/) for semantic similarity
- PDF generation powered by [ReportLab](https://www.reportlab.com/)
- Optimization powered by [PuLP](https://github.com/coin-or/pulp) and [scipy](https://scipy.org/)

---

**Happy Analyzing! 🚀**

