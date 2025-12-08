# Push Code Using GitHub Desktop

## Your Repository
- **GitHub Username:** LilySuffolkU
- **Repository Name:** resume-skills-gap-analyzer
- **Repository URL:** https://github.com/LilySuffolkU/resume-skills-gap-analyzer

## Steps to Push Your Code

### Step 1: Add Your Local Repository
1. Open **GitHub Desktop**
2. Click **"File"** → **"Add Local Repository"**
3. Click **"Choose..."** button
4. Navigate to: `C:\Users\Owner\Desktop\Resume Skills Gap Analyze`
5. Click **"Add Repository"**

### Step 2: Connect to Your GitHub Repository
1. In GitHub Desktop, you should see your files listed
2. At the top, you'll see "Publish repository" button (if not connected yet)
   - OR if it says "Current repository", click the dropdown
   - Select "Publish repository"
3. In the dialog:
   - **Name:** `resume-skills-gap-analyzer`
   - **Owner:** `LilySuffolkU` (should be selected)
   - **Description:** `A Streamlit app that analyzes resume skills gaps against job descriptions`
   - **Keep this code private:** Uncheck (to make it public) OR check (to keep private)
4. Click **"Publish Repository"**

### Step 3: Commit and Push
1. In the bottom left, you'll see a summary of changes
2. In the bottom left text box, type: `Initial commit: Resume Skills Gap Analyzer`
3. Click **"Commit to main"** button
4. Click **"Push origin"** button (top right, or in the menu)

### Alternative: If Repository Already Exists on GitHub
If the repository already exists on GitHub:
1. After adding local repository, click **"Repository"** → **"Repository Settings"**
2. Click **"Remote"** tab
3. Set remote URL to: `https://github.com/LilySuffolkU/resume-skills-gap-analyzer.git`
4. Click **"Save"**
5. Then commit and push as above

## Verify
After pushing, check: https://github.com/LilySuffolkU/resume-skills-gap-analyzer
You should see all your files there!

## Next: Deploy to Streamlit Cloud
Once code is on GitHub:
1. Go to: https://share.streamlit.io
2. Click "New app"
3. Select:
   - **Repository:** `LilySuffolkU/resume-skills-gap-analyzer` (or just `resume-skills-gap-analyzer`)
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** (leave blank or use custom name)
4. Click "Deploy"

