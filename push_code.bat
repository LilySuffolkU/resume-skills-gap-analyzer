@echo off
echo ========================================
echo Pushing Code to GitHub
echo Repository: LilySuffolkU/resume-skills-gap-analyzer
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo.
    echo After installing:
    echo 1. Close and reopen this window
    echo 2. Run this script again
    echo.
    pause
    exit /b 1
)

echo Git is installed!
echo.

REM Initialize if needed
if not exist .git (
    echo Initializing Git repository...
    git init
    echo.
)

echo Adding all files...
git add .

echo.
echo Creating commit...
git commit -m "Initial commit: Resume Skills Gap Analyzer"

echo.
echo Connecting to GitHub repository...
git remote remove origin 2>nul
git remote add origin https://github.com/LilySuffolkU/resume-skills-gap-analyzer.git

echo.
echo Setting main branch...
git branch -M main

echo.
echo ========================================
echo Ready to push!
echo.
echo You will be prompted for your GitHub credentials.
echo.
echo If you use 2FA, you'll need a Personal Access Token instead of password.
echo Get one here: https://github.com/settings/tokens
echo.
echo Press any key to push to GitHub...
echo ========================================
pause

git push -u origin main

echo.
if errorlevel 1 (
    echo.
    echo ERROR: Push failed!
    echo.
    echo Common issues:
    echo - Wrong username/password
    echo - Need Personal Access Token (if 2FA enabled)
    echo - Repository doesn't exist or wrong name
    echo.
    echo Check: https://github.com/LilySuffolkU/resume-skills-gap-analyzer
    echo.
) else (
    echo.
    echo SUCCESS! Your code has been pushed to GitHub!
    echo.
    echo View it at: https://github.com/LilySuffolkU/resume-skills-gap-analyzer
    echo.
    echo Now you can deploy to Streamlit Cloud!
    echo.
)

pause

