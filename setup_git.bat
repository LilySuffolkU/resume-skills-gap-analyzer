@echo off
echo ========================================
echo Resume Skills Gap Analyzer - Git Setup
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo Git is installed!
echo.
echo Initializing Git repository...
git init

echo.
echo Adding all files...
git add .

echo.
echo Creating initial commit...
git commit -m "Initial commit: Resume Skills Gap Analyzer"

echo.
echo ========================================
echo Git repository initialized!
echo.
echo Next steps:
echo 1. Create a repository on GitHub.com
echo 2. Name it: resume-skills-gap-analyzer
echo 3. Run these commands (replace YOUR_USERNAME):
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/resume-skills-gap-analyzer.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo ========================================
pause

