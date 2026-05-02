#!/bin/bash

# ImpactGuard Requirements Installation Script
# Handles dependency installation in correct order

echo "=========================================="
echo "Installing ImpactGuard Dependencies"
echo "=========================================="
echo ""

# Ensure we're in the impactguard environment
if [[ "$CONDA_DEFAULT_ENV" != "impactguard" ]]; then
    echo "⚠️  Warning: Not in 'impactguard' environment"
    echo "Please run: conda activate impactguard"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Step 1: Upgrading pip and installing build tools..."
pip install --upgrade pip setuptools wheel

if [ $? -ne 0 ]; then
    echo "❌ Failed to upgrade pip/setuptools"
    exit 1
fi

echo "✅ Build tools installed"
echo ""

echo "Step 2: Installing core dependencies..."
pip install fastapi uvicorn pydantic pydantic-settings python-multipart python-dotenv

if [ $? -ne 0 ]; then
    echo "❌ Failed to install core dependencies"
    exit 1
fi

echo "✅ Core dependencies installed"
echo ""

echo "Step 3: Installing IBM Watson SDK..."
pip install ibm-watson ibm-cloud-sdk-core

if [ $? -ne 0 ]; then
    echo "❌ Failed to install IBM Watson SDK"
    echo ""
    echo "Troubleshooting:"
    echo "1. Make sure you have the latest setuptools:"
    echo "   pip install --upgrade setuptools"
    echo ""
    echo "2. Try installing with --no-build-isolation:"
    echo "   pip install --no-build-isolation ibm-cloud-sdk-core"
    echo ""
    exit 1
fi

echo "✅ IBM Watson SDK installed"
echo ""

echo "Step 4: Installing remaining dependencies..."
pip install gitpython numpy scikit-learn sentence-transformers pyttsx3 aiofiles

if [ $? -ne 0 ]; then
    echo "❌ Failed to install remaining dependencies"
    exit 1
fi

echo "✅ All dependencies installed"
echo ""

echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "Verify installation:"
echo "  python -c 'import fastapi, ibm_watson; print(\"✅ All imports successful!\")'"
echo ""
echo "Next steps:"
echo "1. Configure IBM WatsonX credentials:"
echo "   cp .env.example .env"
echo "   # Edit .env with your API keys"
echo ""
echo "2. Start the server:"
echo "   python main.py"
echo ""
echo "=========================================="

# Made with Bob
