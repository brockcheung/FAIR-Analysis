# Installation Guide - FAIR Risk Calculator

Multiple installation methods are available to suit your needs.

## Quick Installation (Recommended)

### Linux / macOS
```bash
chmod +x install.sh
./install.sh
```

### Windows
```cmd
install.bat
```

## Installation Methods

### Method 1: Pip Install (Easiest)

**For end users:**
```bash
# Install from the repository
pip install -e .

# Or install specific version
pip install git+https://github.com/brockcheung/FAIR-Analysis.git
```

**After installation, you can run:**
```bash
fair-quick    # Quick analysis tool
fair-calc     # Full interactive calculator
fair-app      # Web application
```

### Method 2: Docker (Most Portable)

**Prerequisites:**
- Docker Desktop installed
- Docker Compose installed

**Steps:**
```bash
# Build and run
docker-compose up

# Or run in background
docker-compose up -d

# Access the web app
# Open browser to http://localhost:8501
```

**Benefits:**
- No Python installation needed
- Consistent environment
- Easy to deploy
- Isolated from system

### Method 3: Manual Installation

**Prerequisites:**
- Python 3.7 or higher
- pip

**Steps:**
```bash
# Clone the repository
git clone https://github.com/brockcheung/FAIR-Analysis.git
cd FAIR-Analysis

# Install dependencies
pip install -r requirements.txt

# Run the tools directly
python quick_risk_analysis.py
python fair_risk_calculator.py
streamlit run fair_risk_app.py
```

### Method 4: Virtual Environment (Recommended for Developers)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Post-Installation Verification

### Test the installation:
```bash
# Quick test
fair-quick --help

# Full calculator test
fair-calc --help

# Web app test
fair-app --help
```

### Run test suite:
```bash
# Run validation tests
python test_validation.py

# Should output: "All tests passed!"
```

## Troubleshooting

### Issue: "Command not found" after pip install

**Solution:**
Make sure Python scripts directory is in your PATH:

**Linux/macOS:**
```bash
export PATH="$HOME/.local/bin:$PATH"
# Add to ~/.bashrc or ~/.zshrc to make permanent
```

**Windows:**
Add to System Environment Variables:
- `%APPDATA%\Python\PythonXX\Scripts`

### Issue: Import errors

**Solution:**
Reinstall dependencies:
```bash
pip install --upgrade -r requirements.txt
```

### Issue: Docker build fails

**Solution:**
```bash
# Clean docker cache
docker-compose down
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

### Issue: Permission denied on Linux/macOS

**Solution:**
```bash
# Install for user only
pip install --user -e .

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Uninstallation

### Pip installation:
```bash
pip uninstall fair-risk-calculator
```

### Docker installation:
```bash
docker-compose down
docker rmi fair-risk-calculator
```

### Manual installation:
```bash
# Just delete the directory
rm -rf FAIR-Analysis
```

## Advanced Options

### Install with development tools:
```bash
pip install -e ".[dev]"
```

This includes:
- pytest (testing)
- pytest-cov (code coverage)
- black (code formatting)
- flake8 (linting)

### Custom installation location:
```bash
pip install --target=/custom/path .
```

### Install specific version:
```bash
pip install fair-risk-calculator==1.0.0
```

## System Requirements

**Minimum:**
- Python 3.7+
- 512 MB RAM
- 100 MB disk space

**Recommended:**
- Python 3.9+
- 2 GB RAM
- 500 MB disk space

**For Docker:**
- Docker Desktop 20.10+
- 4 GB RAM allocated to Docker
- 2 GB disk space

## Platform Support

| Platform | Supported | Notes |
|----------|-----------|-------|
| Linux    | ✅ Yes    | Tested on Ubuntu 20.04+ |
| macOS    | ✅ Yes    | Tested on macOS 11+ |
| Windows  | ✅ Yes    | Tested on Windows 10+ |
| Docker   | ✅ Yes    | All platforms |

## Getting Help

If you encounter issues:

1. Check this guide
2. Review error messages
3. Check Python version: `python --version`
4. Verify pip version: `pip --version`
5. Try reinstalling: `pip install --upgrade --force-reinstall .`
6. Check GitHub issues
7. Run test suite: `python test_validation.py`

## Next Steps

After installation:
1. Read the [README.md](README.md) for usage guide
2. Try the quick analysis: `fair-quick`
3. Run the web app: `fair-app`
4. Explore example scenarios in `scenarios_template.json`
