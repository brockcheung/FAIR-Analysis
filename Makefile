.PHONY: help install install-dev test clean docker-build docker-run docker-stop format lint all

# Default target
help:
	@echo "FAIR Risk Calculator - Makefile Commands"
	@echo "=========================================="
	@echo ""
	@echo "Installation:"
	@echo "  make install          Install the package"
	@echo "  make install-dev      Install with development dependencies"
	@echo ""
	@echo "Running:"
	@echo "  make quick            Run quick analysis tool"
	@echo "  make calc             Run full calculator"
	@echo "  make app              Run web application"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run test suite"
	@echo "  make test-validation  Run validation tests"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build Docker image"
	@echo "  make docker-run       Run Docker container"
	@echo "  make docker-stop      Stop Docker container"
	@echo "  make docker-clean     Remove Docker containers and images"
	@echo ""
	@echo "Development:"
	@echo "  make format           Format code with black"
	@echo "  make lint             Run linting checks"
	@echo "  make clean            Clean generated files"
	@echo ""
	@echo "Package:"
	@echo "  make build            Build distribution packages"
	@echo "  make upload           Upload to PyPI (requires credentials)"
	@echo ""

# Installation targets
install:
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

# Running targets
quick:
	python quick_risk_analysis.py

calc:
	python fair_risk_calculator.py

app:
	streamlit run fair_risk_app.py

# Testing targets
test: test-validation
	@echo "All tests completed!"

test-validation:
	python test_validation.py

test-pytest:
	pytest -v

# Docker targets
docker-build:
	docker-compose build

docker-run:
	docker-compose up

docker-run-bg:
	docker-compose up -d
	@echo "Application running at http://localhost:8501"

docker-stop:
	docker-compose down

docker-clean:
	docker-compose down -v
	docker rmi fair-risk-calculator 2>/dev/null || true

# Development targets
format:
	black fair_risk_calculator.py fair_risk_app.py quick_risk_analysis.py test_validation.py

lint:
	flake8 fair_risk_calculator.py fair_risk_app.py quick_risk_analysis.py --max-line-length=100

# Cleaning targets
clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	rm -rf build dist *.egg-info
	rm -rf outputs charts exports
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

# Build and distribution
build: clean
	python -m build

upload-test: build
	python -m twine upload --repository testpypi dist/*

upload: build
	python -m twine upload dist/*

# Create output directories
dirs:
	mkdir -p outputs charts exports

# Run all checks before commit
check: format lint test
	@echo "All checks passed!"

# Complete setup from scratch
setup: install-dev dirs
	@echo "Setup complete!"

# Run example
example:
	@echo "Running example scenario..."
	python fair_risk_calculator.py --batch scenarios_template.json --export-excel example_output.xlsx
