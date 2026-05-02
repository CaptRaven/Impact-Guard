#!/bin/bash

# Mistral AI Installation Script for ImpactGuard
# This script installs the Mistral AI SDK

echo "🤖 Installing Mistral AI LLM for ImpactGuard..."
echo ""

# Check if conda environment is activated
if [[ -z "$CONDA_DEFAULT_ENV" ]]; then
    echo "⚠️  Warning: No conda environment detected"
    echo "   It's recommended to activate the impactguard environment first:"
    echo "   conda activate impactguard"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Installing Mistral AI SDK..."
pip install mistralai

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Mistral AI SDK installed successfully!"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Get your API key from: https://console.mistral.ai/"
    echo "   2. Add to .env file:"
    echo "      MISTRAL_API_KEY=your_api_key_here"
    echo "   3. Restart the server:"
    echo "      python main.py"
    echo ""
    echo "📚 Read MISTRAL_AI_GUIDE.md for detailed documentation"
else
    echo ""
    echo "❌ Installation failed!"
    echo "   Try manual installation:"
    echo "   pip install mistralai"
    exit 1
fi

# Made with Bob
