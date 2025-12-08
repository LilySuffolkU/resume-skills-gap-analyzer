# GitHub Deployment Guide

## Repository Name Suggestion

**Recommended repository name:** `resume-skills-gap-analyzer`

This name is:
- Clear and descriptive
- Uses hyphens (GitHub best practice)
- All lowercase (GitHub convention)
- SEO-friendly

## Step-by-Step Deployment

### 1. Install Git (if not installed)

Download Git from: https://git-scm.com/download/win

During installation, use default settings.

### 2. Initialize Git Repository

Open PowerShell in your project folder and run:

```powershell
git init
git add .
git commit -m "Initial commit: Resume Skills Gap Analyzer"
```

### 3. Create GitHub Repository

1. Go to https://github.com
2. Sign in (or create account)
3. Click the **"+"** icon in the top right
4. Select **"New repository"**
5. Repository name: `resume-skills-gap-analyzer`
6. Description: "A Streamlit app that analyzes resume skills gaps against job descriptions"
7. Choose **Public** or **Private**
8. **DO NOT** initialize with README, .gitignore, or license (we already have these)
9. Click **"Create repository"**

### 4. Connect and Push to GitHub

After creating the repository, GitHub will show you commands. Use these:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/resume-skills-gap-analyzer.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### 5. Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select:
   - Repository: `resume-skills-gap-analyzer`
   - Branch: `main`
   - Main file path: `app.py`
5. Click **"Deploy"**

Streamlit Cloud will automatically:
- Install dependencies from `requirements.txt`
- Deploy your app
- Give you a public URL

## Alternative Repository Names

If `resume-skills-gap-analyzer` is taken, try:
- `resume-gap-analyzer`
- `skills-gap-analyzer`
- `resume-skills-analyzer`
- `resume-job-matcher`
- `resume-skills-gap-app`

## Notes

- Make sure `requirements.txt` includes all dependencies
- The app will download the SBERT model on first run (this is normal)
- Streamlit Cloud provides free hosting for public repos

