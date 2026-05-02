#!/bin/bash

# ImpactGuard Pre-Push Hook Installer
# Installs the git pre-push hook for automatic code analysis

echo "🛡️  ImpactGuard Pre-Push Hook Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository"
    echo "   Please run this script from the root of your git repository"
    exit 1
fi

# Check if ImpactGuard hook exists
if [ ! -f "hooks/pre-push" ]; then
    echo "❌ Error: hooks/pre-push not found"
    echo "   Make sure you're running this from the ImpactGuard directory"
    exit 1
fi

# Check if hook already exists
if [ -f ".git/hooks/pre-push" ]; then
    echo "⚠️  A pre-push hook already exists"
    echo ""
    cat .git/hooks/pre-push
    echo ""
    read -p "Overwrite existing hook? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled"
        exit 1
    fi
    echo ""
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "⚠️  Warning: 'jq' is not installed. The pre-push hook requires it to parse AI analysis."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   You can install it with: brew install jq"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "   You can install it with: sudo apt install jq"
    fi
    echo ""
    read -p "Continue installation anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled"
        exit 1
    fi
fi

# Copy the hook
echo "📋 Installing pre-push hook..."
cp hooks/pre-push .git/hooks/pre-push

# Make it executable
chmod +x .git/hooks/pre-push

if [ $? -eq 0 ]; then
    echo "✅ Pre-push hook installed successfully!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 What happens now:"
    echo "   1. Every time you run 'git push', ImpactGuard will analyze your changes"
    echo "   2. You'll see AI-powered risk assessment and recommendations"
    echo "   3. You can choose to proceed or cancel the push"
    echo ""
    echo "🔧 Configuration (optional):"
    echo "   export IMPACTGUARD_URL=http://localhost:8000  # Change server URL"
    echo "   export IMPACTGUARD_ENABLED=false              # Disable temporarily"
    echo ""
    echo "🚀 Make sure ImpactGuard server is running:"
    echo "   python main.py"
    echo ""
    echo "🧪 Test it:"
    echo "   1. Make a small change: echo '# test' >> README.md"
    echo "   2. Commit it: git add README.md && git commit -m 'test'"
    echo "   3. Try to push: git push"
    echo "   4. ImpactGuard will analyze before pushing!"
    echo ""
    echo "📚 For more info, see: VSCODE_EXTENSION_GUIDE.md"
    echo ""
else
    echo "❌ Installation failed"
    exit 1
fi

# Made with Bob
