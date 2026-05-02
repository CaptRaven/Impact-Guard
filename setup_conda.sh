#!/bin/bash

# ImpactGuard Conda Environment Setup Script
# This script creates a conda environment and installs all dependencies

echo "=========================================="
echo "ImpactGuard Environment Setup"
echo "=========================================="
echo ""

# Step 1: Create conda environment
echo "Step 1: Creating conda environment 'impactguard' with Python 3.10..."
conda create -n impactguard python=3.10 -y

if [ $? -ne 0 ]; then
    echo "❌ Failed to create conda environment"
    exit 1
fi

echo "✅ Conda environment created successfully"
echo ""

# Step 2: Activate environment and install requirements
echo "Step 2: Activating environment and installing dependencies..."
echo ""

# Get conda base path
CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"

# Activate the environment
conda activate impactguard

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate conda environment"
    exit 1
fi

echo "✅ Environment activated"
echo ""

# Install requirements
echo "Installing Python packages from requirements.txt..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install requirements"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To use ImpactGuard:"
echo "1. Activate the environment:"
echo "   conda activate impactguard"
echo ""
echo "2. Configure your IBM WatsonX credentials:"
echo "   cp .env.example .env"
echo "   # Edit .env and add your API keys"
echo ""
echo "3. Start the server:"
echo "   python main.py"
echo ""
echo "4. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "=========================================="

# Made with Bob
