# Troubleshooting Guide - FAIR Risk Calculator

Common issues and solutions for installing and running the FAIR Risk Calculator.

## 🔴 Issue: Commands Not Recognized (Windows)

### Symptom
After installation, running `fair-quick`, `fair-calc`, or `fair-app` in Command Prompt or PowerShell shows:
```
'fair-quick' is not recognized as an internal or external command,
operable program or batch file.
```

### Root Cause
Python's Scripts directory is not in your Windows PATH.

### ✅ Solution 1: Use Batch Wrapper Scripts (Easiest - Works Immediately)

We provide `.bat` wrapper scripts that work without PATH configuration:

```cmd
# Navigate to the FAIR-Analysis directory
cd path\to\FAIR-Analysis

# Run using the .bat files
fair-quick.bat
fair-calc.bat
fair-app.bat
```

**Benefits:**
- Works immediately, no configuration needed
- No PATH changes required
- Always reliable

### ✅ Solution 2: Use Python Directly (Always Works)

```cmd
cd path\to\FAIR-Analysis
python quick_risk_analysis.py
python fair_risk_calculator.py
streamlit run fair_risk_app.py
```

### ✅ Solution 3: Add Python Scripts to PATH (For Global Access)

To use commands from anywhere, add Python Scripts to your PATH:

#### Find Your Scripts Directory:
```powershell
# In PowerShell, run:
python -c "import sys; import os; print(os.path.join(sys.prefix, 'Scripts'))"

# Or for user install:
python -c "import os; print(os.path.join(os.environ['APPDATA'], 'Python', 'Python' + str(sys.version_info.major) + str(sys.version_info.minor), 'Scripts'))"
```

Typical locations:
- **User install**: `C:\Users\YourName\AppData\Roaming\Python\Python311\Scripts`
- **System install**: `C:\Python311\Scripts` or `C:\Program Files\Python311\Scripts`

#### Add to PATH (Windows 10/11):

**Method A: GUI**
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to **Advanced** tab → **Environment Variables**
3. Under **User variables**, select **Path** → **Edit**
4. Click **New** and paste your Scripts directory path
5. Click **OK** on all windows
6. **Restart Command Prompt/PowerShell** (important!)
7. Test: `fair-quick --help`

**Method B: PowerShell (Admin)**
```powershell
# For user install (replace Python311 with your version)
$scriptsPath = "$env:APPDATA\Python\Python311\Scripts"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$scriptsPath", "User")

# Restart PowerShell and test
fair-quick --help
```

**Method C: Command Prompt (Temporary for current session)**
```cmd
set PATH=%PATH%;%APPDATA%\Python\Python311\Scripts
fair-quick --help
```

## 🔴 Issue: ModuleNotFoundError

### Symptom
```
ModuleNotFoundError: No module named 'numpy'
```

### ✅ Solution
Reinstall dependencies:
```bash
pip install -r requirements.txt

# Or force reinstall
pip install --upgrade --force-reinstall -r requirements.txt
```

## 🔴 Issue: Permission Denied (Windows)

### Symptom
```
ERROR: Could not install packages due to an EnvironmentError: [WinError 5] Access is denied
```

### ✅ Solution

**Option 1: User Install (Recommended)**
```cmd
pip install --user -r requirements.txt
pip install --user -e .
```

**Option 2: Run as Administrator**
- Right-click Command Prompt → Run as administrator
- Then run installation

**Option 3: Virtual Environment**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 🔴 Issue: streamlit: command not found

### Symptom
```
'streamlit' is not recognized as an internal or external command
```

### ✅ Solution

**Option 1: Use Python module syntax**
```cmd
python -m streamlit run fair_risk_app.py
```

**Option 2: Use wrapper script**
```cmd
fair-app.bat
```

**Option 3: Reinstall streamlit**
```cmd
pip install --upgrade streamlit
```

## 🔴 Issue: Import Error After Installation

### Symptom
```
ImportError: cannot import name 'FAIRRiskCalculator'
```

### ✅ Solution
Ensure you're in the correct directory:
```cmd
cd path\to\FAIR-Analysis
python quick_risk_analysis.py
```

Or reinstall in editable mode:
```cmd
pip install -e .
```

## 🔴 Issue: Docker Build Fails

### Symptom
```
ERROR: failed to solve: error getting credentials
```

### ✅ Solution

**Clean Docker and rebuild:**
```bash
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up
```

**Check Docker is running:**
```bash
docker --version
docker ps
```

## 🔴 Issue: Matplotlib Display Error

### Symptom
```
UserWarning: Matplotlib is currently using agg, which is a non-GUI backend
```

### ✅ Solution
This is just a warning. The tool still works and saves plots.

To suppress:
```bash
# Edit the Python file and add at top:
import matplotlib
matplotlib.use('Agg')
```

## 🔴 Issue: Cannot Find test_validation.py

### Symptom
```
Can't open file 'test_validation.py': [Errno 2] No such file or directory
```

### ✅ Solution
Make sure you're in the FAIR-Analysis directory:
```cmd
cd path\to\FAIR-Analysis
python test_validation.py
```

## 🔴 Issue: Excel Export Fails

### Symptom
```
ModuleNotFoundError: No module named 'openpyxl'
```

### ✅ Solution
```bash
pip install openpyxl xlsxwriter
```

## 📋 Verification Checklist

Run these commands to verify your installation:

```bash
# 1. Check Python version (should be 3.7+)
python --version

# 2. Check pip
pip --version

# 3. Navigate to FAIR-Analysis directory
cd path\to\FAIR-Analysis

# 4. Test dependencies
python -c "import numpy, pandas, matplotlib, streamlit; print('All dependencies OK')"

# 5. Run validation tests
python test_validation.py

# 6. Try the tools
python quick_risk_analysis.py
# or
fair-quick.bat
```

## 🔍 Diagnostic Commands

### Check Python Installation
```cmd
python --version
where python
```

### Check pip Installation
```cmd
pip --version
pip list | findstr fair
```

### Check Installed Packages
```cmd
pip show fair-risk-calculator
pip list
```

### Check PATH (PowerShell)
```powershell
$env:Path -split ';' | Select-String "Python"
```

### Check PATH (Command Prompt)
```cmd
echo %PATH%
```

### Find Python Scripts Directory
```powershell
python -c "import sys, os; print(os.path.join(sys.prefix, 'Scripts'))"
```

## 🆘 Still Having Issues?

### Try Complete Reinstall

```cmd
# 1. Uninstall
pip uninstall fair-risk-calculator -y

# 2. Clean cache
pip cache purge

# 3. Reinstall dependencies
pip install --no-cache-dir -r requirements.txt

# 4. Reinstall package
pip install --user -e .

# 5. Use wrapper scripts
fair-quick.bat
```

### Alternative: Fresh Virtual Environment

```cmd
# Create new virtual environment
python -m venv venv_fair

# Activate it
venv_fair\Scripts\activate

# Install
pip install -r requirements.txt

# Run
python quick_risk_analysis.py
```

## 💡 Best Practices

1. **Always use wrapper scripts (.bat files) on Windows** - Most reliable
2. **Stay in the project directory** when running tools
3. **Use virtual environments** for isolation
4. **Keep Python updated** (but not too bleeding edge)
5. **Restart terminal** after PATH changes
6. **Check firewall** if Docker has issues

## 🪟 Windows-Specific Tips

### PowerShell Execution Policy
If scripts don't run in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Long Path Support
Enable long paths (Windows 10+):
```
1. Run: gpedit.msc
2. Navigate: Computer Config > Admin Templates > System > Filesystem
3. Enable: "Enable Win32 long paths"
```

### Antivirus Interference
If installation is slow or fails:
- Temporarily disable antivirus
- Add Python and FAIR-Analysis folder to exclusions

## 🐧 Linux-Specific Tips

### Permission Issues
```bash
chmod +x install.sh
./install.sh
```

### Path for User Install
```bash
export PATH="$HOME/.local/bin:$PATH"
# Add to ~/.bashrc or ~/.zshrc for permanent
```

## 🍎 macOS-Specific Tips

### Python Version Conflicts
```bash
# Use python3 explicitly
python3 --version
python3 -m pip install -r requirements.txt
```

### Command Not Found
```bash
# Add to PATH in ~/.zshrc or ~/.bash_profile
export PATH="$HOME/Library/Python/3.x/bin:$PATH"
source ~/.zshrc
```

## 📞 Getting More Help

If none of these solutions work:

1. **Check the error message carefully** - Often contains the solution
2. **Run diagnostics** (commands above) and note the output
3. **Check Python version** - Must be 3.7 or higher
4. **Try Docker** - Eliminates most environment issues
5. **Use virtual environment** - Isolates dependencies

## Summary: Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Command not found (Windows) | Use `fair-quick.bat` instead |
| Command not found (Linux/Mac) | Add `~/.local/bin` to PATH |
| Import errors | `pip install -r requirements.txt` |
| Permission denied | Use `--user` flag or virtual environment |
| PATH issues | Use `.bat` files or Python directly |
| Streamlit errors | `python -m streamlit run fair_risk_app.py` |
| Everything broken | Try Docker: `docker-compose up` |

**Remember: The .bat wrapper scripts work immediately on Windows without any configuration!**
