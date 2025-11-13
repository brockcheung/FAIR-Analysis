#!/usr/bin/env python3
"""
Setup script for FAIR Risk Calculator
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="fair-risk-calculator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Interactive FAIR (Factor Analysis of Information Risk) risk assessment tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brockcheung/FAIR-Analysis",
    packages=find_packages(exclude=["tests", "tests.*"]),
    py_modules=[
        "fair_risk_calculator",
        "fair_risk_app",
        "quick_risk_analysis",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "fair-calc=fair_risk_calculator:main",
            "fair-quick=quick_risk_analysis:main",
            "fair-app=fair_risk_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["scenarios_template.json", "*.md"],
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    keywords="fair risk analysis cybersecurity monte-carlo simulation security",
    project_urls={
        "Bug Reports": "https://github.com/brockcheung/FAIR-Analysis/issues",
        "Source": "https://github.com/brockcheung/FAIR-Analysis",
    },
)
