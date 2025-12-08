# Installation Guide - Resume Skills Gap Analyzer

## Issue: Connection Refused / Python Not Found

If you're seeing connection errors, it's likely because:
1. Python is not installed
2. Dependencies are not installed
3. Python is not in your system PATH

## Step-by-Step Installation

### Option 1: Install Python (Recommended)

1. **Download Python 3.8 or higher**
   - Go to https://www.python.org/downloads/
   - Download the latest Python 3.x version
   - **IMPORTANT**: During installation, check "Add Python to PATH"

2. **Verify Installation**
   - Open a new PowerShell/Command Prompt
   - Run: `python --version`
   - You should see something like: `Python 3.11.x`

3. **Install Dependencies**
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python -m streamlit run app.py
   ```

### Option 2: Use Anaconda/Miniconda

1. **Install Anaconda** from https://www.anaconda.com/products/distribution

2. **Open Anaconda Prompt**

3. **Navigate to project directory**
   ```bash
   cd "C:\Users\Owner\Desktop\Resume Skills Gap Analyze"
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

### Option 3: Use the Batch Script

1. **Double-click `setup_and_run.bat`**
   - This will check for Python, install dependencies, and run the app

## Troubleshooting

### If Python is installed but not found:
1. Find where Python is installed (usually `C:\Users\YourName\AppData\Local\Programs\Python\`)
2. Add it to your system PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" variable
   - Add Python installation folder and `Scripts` folder

### If dependencies fail to install:
- Try: `python -m pip install --user -r requirements.txt`
- Or install individually:
  ```bash
  python -m pip install streamlit
  python -m pip install python-docx
  python -m pip install PyPDF2
  python -m pip install sentence-transformers
  python -m pip install scikit-learn
  python -m pip install reportlab
  python -m pip install numpy pandas
  ```

### If Streamlit starts but connection is refused:
- Check if port 8501 is already in use
- Try: `streamlit run app.py --server.port 8502`
- Or check firewall settings

## Quick Test

After installation, test with:
```bash
python -c "import streamlit; print('Streamlit OK')"
```

If this works, you're ready to run the app!

