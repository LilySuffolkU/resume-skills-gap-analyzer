# Push Code to GitHub - Instructions

## Your Repository Details
- **GitHub Username:** LilySuffolkU
- **Repository Name:** resume-skills-gap-analyzer
- **Repository URL:** https://github.com/LilySuffolkU/resume-skills-gap-analyzer

## Option 1: Install Git and Push (Recommended)

### Step 1: Install Git
1. Download from: https://git-scm.com/download/win
2. Install with default settings
3. **Close and reopen PowerShell** (important!)

### Step 2: Push Your Code
After installing Git and reopening PowerShell, run these commands:

```powershell
cd "C:\Users\Owner\Desktop\Resume Skills Gap Analyze"

# Initialize Git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Resume Skills Gap Analyzer"

# Connect to your GitHub repository
git remote add origin https://github.com/LilySuffolkU/resume-skills-gap-analyzer.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

You'll be prompted for your GitHub username and password (or personal access token).

## Option 2: Use GitHub Desktop (Easier)

1. Download GitHub Desktop: https://desktop.github.com/
2. Install it
3. Sign in with your GitHub account (LilySuffolkU)
4. In GitHub Desktop:
   - Click "File" → "Add Local Repository"
   - Browse to: `C:\Users\Owner\Desktop\Resume Skills Gap Analyze`
   - Click "Add Repository"
   - Click "Publish repository" button
   - Make sure it says: `LilySuffolkU/resume-skills-gap-analyzer`
   - Click "Publish Repository"

## Option 3: Use GitHub Web Interface (Upload Files)

1. Go to: https://github.com/LilySuffolkU/resume-skills-gap-analyzer
2. Click "uploading an existing file"
3. Drag and drop all your project files
4. Scroll down and click "Commit changes"

---

## After Pushing

Once your code is on GitHub, go back to Streamlit Cloud:
- Repository: `LilySuffolkU/resume-skills-gap-analyzer` or just `resume-skills-gap-analyzer`
- Branch: `main`
- Main file path: `app.py`

