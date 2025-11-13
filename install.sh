#!/bin/bash
###############################################################################
# FAIR Risk Calculator - Installation Script
# Supports Linux and macOS
###############################################################################

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║      FAIR Risk Calculator - Installation Script           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check Python version
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.7 or higher."
    exit 1
fi

# Check pip
echo "Checking pip installation..."
if command -v pip3 &> /dev/null; then
    print_success "pip3 found"
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    print_success "pip found"
    PIP_CMD="pip"
else
    print_error "pip not found. Please install pip."
    exit 1
fi

# Ask for installation type
echo ""
echo "Select installation type:"
echo "  1) User installation (recommended)"
echo "  2) System-wide installation (requires sudo)"
echo "  3) Development installation (editable mode)"
echo "  4) Docker installation"
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        print_info "Installing for current user..."
        $PIP_CMD install --user -r requirements.txt
        $PIP_CMD install --user -e .
        print_success "Installation complete!"
        echo ""
        echo "You can now run:"
        echo "  fair-quick    # Quick analysis tool"
        echo "  fair-calc     # Full calculator"
        echo "  fair-app      # Web application"
        ;;
    2)
        print_info "Installing system-wide (requires sudo)..."
        sudo $PIP_CMD install -r requirements.txt
        sudo $PIP_CMD install .
        print_success "Installation complete!"
        echo ""
        echo "You can now run:"
        echo "  fair-quick    # Quick analysis tool"
        echo "  fair-calc     # Full calculator"
        echo "  fair-app      # Web application"
        ;;
    3)
        print_info "Installing in development mode..."
        $PIP_CMD install --user -r requirements.txt
        $PIP_CMD install --user -e ".[dev]"
        print_success "Development installation complete!"
        echo ""
        echo "You can now run:"
        echo "  python fair_risk_calculator.py"
        echo "  python quick_risk_analysis.py"
        echo "  streamlit run fair_risk_app.py"
        ;;
    4)
        print_info "Setting up Docker installation..."
        if ! command -v docker &> /dev/null; then
            print_error "Docker not found. Please install Docker first."
            exit 1
        fi

        if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
            print_error "Docker Compose not found. Please install Docker Compose first."
            exit 1
        fi

        print_info "Building Docker image..."
        docker-compose build
        print_success "Docker installation complete!"
        echo ""
        echo "To run the application:"
        echo "  docker-compose up"
        echo ""
        echo "Then open your browser to: http://localhost:8501"
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                 Installation Complete!                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Quick Start:"
echo "  1. Try quick analysis:  fair-quick"
echo "  2. Run web app:         fair-app"
echo "  3. Full calculator:     fair-calc"
echo ""
echo "For help, run any command with --help"
echo ""
