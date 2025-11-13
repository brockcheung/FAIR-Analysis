# Packaging and Distribution Guide

This document explains how the FAIR Risk Calculator is packaged and how to use it in different environments.

## Package Overview

The FAIR Risk Calculator is distributed as a Python package that can be installed via:
- **pip** (Python Package Index)
- **Docker** (Containerized application)
- **Git clone** (Direct source)
- **Standalone executable** (Coming soon)

## Quick Start

### Option 1: One-Line Install
```bash
# Linux/macOS
curl -sSL https://raw.githubusercontent.com/brockcheung/FAIR-Analysis/main/install.sh | bash

# Or download and run
chmod +x install.sh && ./install.sh
```

### Option 2: Docker (Zero Setup)
```bash
docker-compose up
# Visit http://localhost:8501
```

### Option 3: Pip Install
```bash
pip install -e .
```

## Distribution Formats

### 1. Python Package

**Structure:**
```
fair-risk-calculator/
├── setup.py              # Legacy setup
├── pyproject.toml        # Modern Python packaging
├── requirements.txt      # Dependencies
├── fair_risk_calculator.py
├── fair_risk_app.py
├── quick_risk_analysis.py
└── test_validation.py
```

**Installation:**
```bash
# From source
pip install -e .

# From GitHub
pip install git+https://github.com/brockcheung/FAIR-Analysis.git

# From PyPI (when published)
pip install fair-risk-calculator
```

**Entry Points:**
After installation, these commands are available:
- `fair-quick` - Quick analysis tool
- `fair-calc` - Full calculator
- `fair-app` - Web application

### 2. Docker Container

**Structure:**
```
Dockerfile              # Container definition
docker-compose.yml      # Orchestration
```

**Usage:**
```bash
# Build
docker-compose build

# Run
docker-compose up

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

**Image Details:**
- Base: Python 3.10-slim
- Size: ~500MB
- Includes all dependencies
- Exposes port 8501 (Streamlit)
- Persistent volumes for outputs

### 3. Source Installation

**Clone and run:**
```bash
git clone https://github.com/brockcheung/FAIR-Analysis.git
cd FAIR-Analysis
pip install -r requirements.txt
python quick_risk_analysis.py
```

## Advanced Packaging

### Building Distribution Packages

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# This creates:
# - dist/fair_risk_calculator-1.0.0.tar.gz (source)
# - dist/fair_risk_calculator-1.0.0-py3-none-any.whl (wheel)
```

### Publishing to PyPI

```bash
# Test on TestPyPI first
python -m twine upload --repository testpypi dist/*

# Then publish to PyPI
python -m twine upload dist/*
```

### Creating Docker Images

```bash
# Build image
docker build -t fair-risk-calculator:1.0.0 .

# Tag for registry
docker tag fair-risk-calculator:1.0.0 username/fair-risk-calculator:1.0.0

# Push to Docker Hub
docker push username/fair-risk-calculator:1.0.0
```

## Environment-Specific Deployments

### Development Environment

```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install in editable mode with dev tools
pip install -e ".[dev]"

# Run tests
pytest
```

### Production Environment

```bash
# Use Docker for consistency
docker-compose -f docker-compose.prod.yml up -d

# Or systemd service on Linux
sudo systemctl enable fair-risk-app
sudo systemctl start fair-risk-app
```

### Cloud Deployments

#### AWS
```bash
# Using AWS ECS
aws ecs create-service --cluster fair-cluster \
  --service-name fair-app \
  --task-definition fair-risk-calculator:1

# Or AWS Elastic Beanstalk
eb init fair-risk-calculator
eb create fair-env
eb deploy
```

#### Google Cloud
```bash
# Using Cloud Run
gcloud run deploy fair-risk-calculator \
  --image gcr.io/PROJECT/fair-risk-calculator \
  --platform managed
```

#### Azure
```bash
# Using Azure Container Instances
az container create \
  --resource-group fair-rg \
  --name fair-app \
  --image fair-risk-calculator:1.0.0 \
  --ports 8501
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fair-risk-calculator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fair
  template:
    metadata:
      labels:
        app: fair
    spec:
      containers:
      - name: fair-app
        image: fair-risk-calculator:1.0.0
        ports:
        - containerPort: 8501
---
apiVersion: v1
kind: Service
metadata:
  name: fair-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8501
  selector:
    app: fair
```

## Dependency Management

### Requirements Files

**requirements.txt** - Core dependencies
```
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
streamlit>=1.25.0
plotly>=5.10.0
xlsxwriter>=3.0.0
openpyxl>=3.0.0
```

**requirements-dev.txt** - Development dependencies
```
pytest>=7.0.0
pytest-cov>=3.0.0
black>=22.0.0
flake8>=4.0.0
```

### Dependency Locking

```bash
# Generate locked requirements
pip freeze > requirements-lock.txt

# Install from locked requirements
pip install -r requirements-lock.txt
```

## Version Management

### Semantic Versioning

We follow SemVer: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Updating Version

Update in both:
1. `setup.py` - `version="1.0.0"`
2. `pyproject.toml` - `version = "1.0.0"`

### Git Tags

```bash
# Create version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - run: pip install -r requirements.txt
    - run: python test_validation.py
```

## Distribution Checklist

Before releasing:

- [ ] All tests pass
- [ ] Version numbers updated
- [ ] CHANGELOG.md updated
- [ ] README.md reviewed
- [ ] Documentation complete
- [ ] Docker image builds
- [ ] PyPI package builds
- [ ] Git tag created
- [ ] Release notes written

## Troubleshooting Packaging Issues

### Issue: Package not found after install

**Check:**
```bash
pip show fair-risk-calculator
which fair-quick
```

**Fix:**
```bash
pip install --force-reinstall -e .
```

### Issue: Docker build fails

**Solution:**
```bash
docker system prune -a
docker-compose build --no-cache
```

### Issue: Import errors

**Check Python path:**
```bash
python -c "import sys; print('\n'.join(sys.path))"
```

**Fix:**
```bash
pip uninstall fair-risk-calculator
pip install -e .
```

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [Docker Documentation](https://docs.docker.com/)
- [Streamlit Deployment](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)
