# Deploy to Streamlit Cloud - Quick Guide

## ✅ Pre-Deployment Checklist

Your repository is already connected to GitHub:
- ✅ Repository: `https://github.com/LilySuffolkU/resume-skills-gap-analyzer`
- ✅ All code is committed and pushed
- ✅ `requirements.txt` is complete
- ✅ `app.py` is the main file

## 🚀 Deployment Steps

### 1. Go to Streamlit Cloud
Visit: **https://share.streamlit.io**

### 2. Sign In
- Click "Continue to sign-in"
- Sign in with your **GitHub account** (LilySuffolkU)

### 3. Create New App
- Click **"New app"** button
- Fill in the form:
  - **Repository**: Select `LilySuffolkU/resume-skills-gap-analyzer`
  - **Branch**: `main`
  - **Main file path**: `app.py`
- Click **"Deploy"**

### 4. Wait for Deployment
Streamlit Cloud will:
- Install all dependencies from `requirements.txt`
- Deploy your app
- Provide a public URL (usually takes 2-5 minutes)

### 5. Access Your App
Once deployed, you'll get a URL like:
```
https://resume-skills-gap-analyzer.streamlit.app
```

## 📝 Notes

- **First Run**: The app will download the SBERT model (`all-MiniLM-L6-v2`) on first use - this is normal and takes a few minutes
- **spaCy Model**: The app will download `en_core_web_sm` automatically if needed
- **Free Tier**: Streamlit Cloud offers free hosting for public repositories
- **Updates**: Any push to the `main` branch will automatically redeploy your app

## 🔧 Troubleshooting

### If deployment fails:
1. Check that `requirements.txt` includes all dependencies
2. Verify `app.py` is in the root directory
3. Check the deployment logs in Streamlit Cloud dashboard

### If the app loads but has errors:
1. Check the app logs in Streamlit Cloud
2. Ensure all data files (`data/skill_dictionary.json`, `data/job_role_templates.json`) are in the repository
3. Verify all utility files in `utils/` are present

## 🎉 After Deployment

Update your README.md with the live app URL:
```markdown
**🌐 Live Application:** https://your-app-name.streamlit.app
```

Replace `your-app-name` with your actual Streamlit Cloud app name.

