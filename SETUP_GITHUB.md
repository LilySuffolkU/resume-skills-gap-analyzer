# Complete GitHub Setup Guide

## Step 1: Install Git

1. **Download Git for Windows:**
   - Go to: https://git-scm.com/download/win
   - Download the installer
   - Run the installer
   - **Use all default settings** (just click Next/Install)

2. **After installation:**
   - **Close and reopen** your PowerShell/terminal window
   - This is important so Git is added to your PATH

## Step 2: Create GitHub Account (if needed)

1. Go to: https://github.com
2. Sign up for a free account (if you don't have one)
3. Verify your email address

## Step 3: Initialize Git Repository Locally

After Git is installed and you've reopened PowerShell, run these commands:

```powershell
cd "C:\Users\Owner\Desktop\Resume Skills Gap Analyze"
git init
git add .
git commit -m "Initial commit: Resume Skills Gap Analyzer"
```

## Step 4: Create Repository on GitHub

1. Go to: https://github.com/new
2. Fill in:
   - **Repository name:** `resume-skills-gap-analyzer`
   - **Description:** `A Streamlit app that analyzes resume skills gaps against job descriptions`
   - **Visibility:** Choose Public or Private
   - **DO NOT** check "Add a README file" (we already have one)
   - **DO NOT** add .gitignore or license (we have .gitignore)
3. Click **"Create repository"**

## Step 5: Connect and Push to GitHub

After creating the repository, GitHub will show you commands. Use these:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/resume-skills-gap-analyzer.git
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username.**

You'll be prompted for your GitHub username and password (or personal access token).

## Step 6: Deploy to Streamlit Cloud

Now go back to https://share.streamlit.io and deploy:

- **Repository:** `resume-skills-gap-analyzer`
- **Branch:** `main`
- **Main file path:** `app.py`
- **App URL:** (leave blank or use custom name)

---

## Quick Reference

**Repository Name:** `resume-skills-gap-analyzer`

**If that name is taken, try:**
- `resume-gap-analyzer`
- `skills-gap-analyzer`
- `resume-skills-analyzer`
- `resume-job-matcher`

