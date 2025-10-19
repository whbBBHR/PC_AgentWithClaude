#!/bin/bash

# PC Agent with Claude - Installation Script
# Installs dependencies and sets up the computer-using agent

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

print_status "PC Agent with Claude - Installation Starting..."

# Detect operating system
OS=$(detect_os)
print_status "Detected OS: $OS"

# Check Python installation
if ! command_exists python3; then
    print_error "Python 3 is required but not installed!"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
print_status "Python version: $PYTHON_VERSION"

# Check if Python version is 3.8 or higher
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    print_error "Python 3.8 or higher is required!"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install core dependencies
print_status "Installing core Python dependencies..."
pip install -r requirements.txt

# OS-specific installations
case $OS in
    "linux")
        print_status "Installing Linux-specific dependencies..."
        
        # Check for apt (Debian/Ubuntu)
        if command_exists apt; then
            print_status "Installing system dependencies with apt..."
            sudo apt update
            sudo apt install -y \
                tesseract-ocr \
                tesseract-ocr-eng \
                libgl1-mesa-glx \
                libglib2.0-0 \
                libsm6 \
                libxext6 \
                libxrender-dev \
                libgomp1 \
                xvfb
        
        # Check for yum (RedHat/CentOS)
        elif command_exists yum; then
            print_status "Installing system dependencies with yum..."
            sudo yum install -y \
                tesseract \
                tesseract-langpack-eng \
                mesa-libGL \
                glib2 \
                libSM \
                libXext \
                libXrender \
                libgomp \
                xorg-x11-server-Xvfb
        else
            print_warning "Could not detect package manager. Please install tesseract-ocr and OpenCV dependencies manually."
        fi
        ;;
        
    "macos")
        print_status "Installing macOS-specific dependencies..."
        
        if command_exists brew; then
            print_status "Installing dependencies with Homebrew..."
            brew install tesseract
            
            # Install Chrome if not present (for Selenium)
            if ! [ -d "/Applications/Google Chrome.app" ]; then
                print_status "Chrome not found. Please install Chrome for web automation."
                print_status "Download from: https://www.google.com/chrome/"
            fi
        else
            print_warning "Homebrew not found. Please install tesseract manually:"
            print_warning "  brew install tesseract"
            print_warning "Or download from: https://github.com/tesseract-ocr/tesseract"
        fi
        ;;
        
    "windows")
        print_status "Windows detected. Please ensure the following are installed:"
        print_warning "1. Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki"
        print_warning "2. Google Chrome (for web automation)"
        print_warning "3. Visual C++ Redistributable (for OpenCV)"
        ;;
        
    *)
        print_warning "Unknown OS. Please install dependencies manually."
        ;;
esac

# Download ChromeDriver if needed
print_status "Checking ChromeDriver..."
if ! command_exists chromedriver; then
    print_status "ChromeDriver not found in PATH. Installing via webdriver-manager..."
    pip install webdriver-manager
    print_success "WebDriver manager installed (will auto-download ChromeDriver)"
else
    print_success "ChromeDriver found in PATH"
fi

# Create configuration file if it doesn't exist
if [ ! -f "config.json" ]; then
    print_status "Creating configuration file..."
    cp config.example.json config.json
    print_success "Configuration file created: config.json"
    print_warning "Please edit config.json and add your Anthropic API key!"
else
    print_status "Configuration file already exists"
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p screenshots
mkdir -p logs
mkdir -p temp
print_success "Directories created"

# Set up git ignore if git repository exists
if [ -d ".git" ]; then
    if [ ! -f ".gitignore" ]; then
        print_status "Creating .gitignore file..."
        cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environment
venv/
env/
ENV/

# Configuration and secrets
config.json
.env
*.key

# Logs
logs/
*.log

# Screenshots and temporary files
screenshots/
temp/
*.tmp

# OS specific
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Browser data
chromedriver*
geckodriver*
EOF
        print_success ".gitignore created"
    fi
fi

# Test installation
print_status "Testing installation..."

# Test basic imports
python3 -c "
import sys
print(f'Python version: {sys.version}')

# Test core imports
try:
    import cv2
    print('✓ OpenCV imported successfully')
except ImportError as e:
    print(f'✗ OpenCV import failed: {e}')

try:
    import pyautogui
    print('✓ PyAutoGUI imported successfully')
except ImportError as e:
    print(f'✗ PyAutoGUI import failed: {e}')

try:
    import anthropic
    print('✓ Anthropic imported successfully')
except ImportError as e:
    print(f'✗ Anthropic import failed: {e}')

try:
    from selenium import webdriver
    print('✓ Selenium imported successfully')
except ImportError as e:
    print(f'✗ Selenium import failed: {e}')

try:
    import numpy as np
    print('✓ NumPy imported successfully')
except ImportError as e:
    print(f'✗ NumPy import failed: {e}')

try:
    from PIL import Image
    print('✓ Pillow imported successfully')
except ImportError as e:
    print(f'✗ Pillow import failed: {e}')
"

echo
print_success "Installation completed!"
echo
print_status "Next steps:"
echo "1. Edit config.json and add your Anthropic API key"
echo "2. Run a test: python3 -m src.pc_agent.computer_agent"
echo "3. Check the examples/ directory for usage examples"
echo
print_warning "Important notes:"
echo "• Make sure to activate the virtual environment: source venv/bin/activate"
echo "• Keep your API keys secure and never commit them to version control"
echo "• Test with simple tasks first before complex automation"
echo
print_success "Happy automating! 🤖"