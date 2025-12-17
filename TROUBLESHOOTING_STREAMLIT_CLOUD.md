# Troubleshooting Streamlit Cloud Deployment

## If the app is not working on Streamlit Cloud, follow these steps:

### Step 1: Check Streamlit Cloud Dashboard

1. Go to **https://share.streamlit.io**
2. Sign in with your GitHub account
3. Find your app: `resume-skills-gap-analyzer`
4. Click on it to view details

### Step 2: Check the Logs

1. In the app dashboard, click on **"Logs"** or **"View logs"**
2. Look for error messages (usually in red)
3. Common errors:
   - `ModuleNotFoundError` - Missing dependency
   - `FileNotFoundError` - Missing data file
   - `ImportError` - Import issue

### Step 3: Force Redeploy

1. In the Streamlit Cloud dashboard
2. Click the **three dots (⋮)** next to your app
3. Select **"Reboot app"** or **"Redeploy"**
4. Wait 2-5 minutes for redeployment

### Step 4: Verify Repository Contents

Make sure these files are in your GitHub repository:
- ✅ `app.py` (main file)
- ✅ `requirements.txt` (with all dependencies)
- ✅ `data/skill_dictionary.json`
- ✅ `data/job_role_templates.json`
- ✅ `utils/` folder with all Python files

### Step 5: Check Requirements.txt

Your `requirements.txt` should include:
```
streamlit
spacy
python-docx
PyPDF2
numpy
pandas
sentence-transformers
scikit-learn
reportlab
pulp
scipy
```

### Step 6: Common Issues and Fixes

#### Issue: "ModuleNotFoundError: No module named 'utils.optimization'"
**Fix:** Make sure `utils/optimization.py` is in your repository

#### Issue: "FileNotFoundError: data/skill_dictionary.json"
**Fix:** Ensure all files in the `data/` folder are committed to Git

#### Issue: App shows blank page or loading forever
**Fix:** 
- Check logs for errors
- Make sure `app.py` has `if __name__ == "__main__": main()` at the end
- Verify all imports work

#### Issue: "ImportError: cannot import name 'X'"
**Fix:** Check that all functions are properly defined in the utils files

### Step 7: Manual Redeploy

If automatic redeploy doesn't work:

1. Go to **https://share.streamlit.io**
2. Click **"New app"**
3. Select your repository: `LilySuffolkU/resume-skills-gap-analyzer`
4. Branch: `main`
5. Main file: `app.py`
6. Click **"Deploy"**

### Step 8: Check App URL

After deployment, your app URL should be:
- Format: `https://[app-name]-[random-id].streamlit.app`
- Or: `https://[app-name].streamlit.app` (if you set a custom name)

### Step 9: Test Locally First

Before deploying, test locally:
```bash
streamlit run app.py
```

If it works locally but not on Streamlit Cloud, the issue is likely:
- Missing files in repository
- Different Python version
- Missing dependencies

### Step 10: Contact Support

If nothing works:
1. Check Streamlit Cloud status: https://status.streamlit.io
2. Review Streamlit Cloud docs: https://docs.streamlit.io/streamlit-community-cloud
3. Check GitHub Issues for similar problems

## Quick Checklist

- [ ] All files committed to Git
- [ ] All files pushed to GitHub
- [ ] `requirements.txt` includes all dependencies
- [ ] `app.py` is in the root directory
- [ ] `data/` folder exists with JSON files
- [ ] `utils/` folder exists with all Python files
- [ ] App works locally (`streamlit run app.py`)
- [ ] Streamlit Cloud app is set to deploy from `main` branch
- [ ] Main file path is set to `app.py`

## Still Not Working?

Share the error message from the Streamlit Cloud logs, and I can help troubleshoot further!

