# 🔌 VS Code Extension Integration Guide

## Overview

ImpactGuard can be integrated as a **pre-push analysis tool** in VS Code, providing AI-powered code review before developers push to git.

## 🎯 Use Case

**Developer Workflow:**
1. Developer makes code changes
2. Developer attempts to push to git
3. **ImpactGuard analyzes changes automatically**
4. Developer reviews AI insights before confirming push
5. Developer makes informed decision

## 🚀 Integration Options

### Option 1: Git Pre-Push Hook (Recommended)

Automatically analyze code before every `git push`.

#### Setup:

1. **Create the hook file:**
```bash
# Navigate to your repository
cd /path/to/your/repo

# Create pre-push hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash

echo "🛡️ ImpactGuard: Analyzing changes before push..."
echo ""

# Get list of changed files
CHANGED_FILES=$(git diff --name-only origin/$(git rev-parse --abbrev-ref HEAD)..HEAD)

if [ -z "$CHANGED_FILES" ]; then
    echo "✅ No changes to analyze"
    exit 0
fi

# Call ImpactGuard API
RESPONSE=$(curl -s -X POST http://localhost:8000/llm/explain-risk \
  -H "Content-Type: application/json" \
  -d "{
    \"repository_path\": \"$(pwd)\",
    \"file_paths\": $(echo "$CHANGED_FILES" | jq -R -s -c 'split("\n")[:-1]'),
    \"include_code\": true
  }")

# Check if Mistral AI is enabled
LLM_ENABLED=$(echo "$RESPONSE" | jq -r '.llm_enabled')

if [ "$LLM_ENABLED" = "true" ]; then
    echo "🤖 AI Analysis:"
    echo "$RESPONSE" | jq -r '.explanation'
else
    echo "⚠️  Mistral AI not configured. Using basic analysis."
fi

echo ""
echo "📊 Risk Level: $(echo "$RESPONSE" | jq -r '.risk_level')"
echo "📈 Risk Score: $(echo "$RESPONSE" | jq -r '.risk_score')"
echo ""

# Ask for confirmation
read -p "Continue with push? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Push cancelled"
    exit 1
fi

echo "✅ Proceeding with push..."
exit 0
EOF

# Make it executable
chmod +x .git/hooks/pre-push
```

2. **Test it:**
```bash
# Make a change
echo "# test" >> README.md
git add README.md
git commit -m "test"

# Try to push - ImpactGuard will analyze first!
git push
```

### Option 2: VS Code Task

Create a VS Code task for manual analysis.

#### Setup:

1. **Create `.vscode/tasks.json`:**
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "ImpactGuard: Analyze Changes",
      "type": "shell",
      "command": "bash",
      "args": [
        "-c",
        "git diff --name-only HEAD | jq -R -s -c 'split(\"\\n\")[:-1]' | xargs -I {} curl -s -X POST http://localhost:8000/llm/explain-risk -H 'Content-Type: application/json' -d '{\"repository_path\": \"${workspaceFolder}\", \"file_paths\": {}, \"include_code\": true}' | jq -r '.explanation'"
      ],
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "ImpactGuard: Quick Summary",
      "type": "shell",
      "command": "bash",
      "args": [
        "-c",
        "git diff --name-only HEAD | jq -R -s -c 'split(\"\\n\")[:-1]' | xargs -I {} curl -s -X POST http://localhost:8000/llm/conversational-summary -H 'Content-Type: application/json' -d '{\"repository_path\": \"${workspaceFolder}\", \"file_paths\": {}}' | jq -r '.summary'"
      ],
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "ImpactGuard: Get Fix Suggestions",
      "type": "shell",
      "command": "bash",
      "args": [
        "-c",
        "git diff --name-only HEAD | jq -R -s -c 'split(\"\\n\")[:-1]' | xargs -I {} curl -s -X POST http://localhost:8000/llm/suggest-fixes -H 'Content-Type: application/json' -d '{\"repository_path\": \"${workspaceFolder}\", \"file_paths\": {}}' | jq '.suggestions'"
      ],
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

2. **Use it:**
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
- Type "Tasks: Run Task"
- Select "ImpactGuard: Analyze Changes"

### Option 3: VS Code Keybindings

Add keyboard shortcuts for quick access.

#### Setup:

1. **Create `.vscode/keybindings.json`:**
```json
[
  {
    "key": "ctrl+shift+i",
    "command": "workbench.action.tasks.runTask",
    "args": "ImpactGuard: Analyze Changes"
  },
  {
    "key": "ctrl+shift+s",
    "command": "workbench.action.tasks.runTask",
    "args": "ImpactGuard: Quick Summary"
  },
  {
    "key": "ctrl+shift+f",
    "command": "workbench.action.tasks.runTask",
    "args": "ImpactGuard: Get Fix Suggestions"
  }
]
```

2. **Use it:**
- `Ctrl+Shift+I` - Full AI analysis
- `Ctrl+Shift+S` - Quick summary
- `Ctrl+Shift+F` - Get fix suggestions

## 🎨 Custom VS Code Extension (Advanced)

For a fully integrated experience, create a custom VS Code extension.

### Extension Structure:

```
impactguard-vscode/
├── package.json
├── src/
│   ├── extension.ts
│   ├── impactGuardClient.ts
│   └── views/
│       ├── analysisPanel.ts
│       └── riskIndicator.ts
└── README.md
```

### Key Features:

1. **Status Bar Indicator**
   - Shows risk level of current changes
   - Click to see detailed analysis

2. **Analysis Panel**
   - Side panel with AI insights
   - Real-time updates as you code

3. **Inline Warnings**
   - Highlight risky lines in editor
   - Show AI suggestions on hover

4. **Pre-Push Dialog**
   - Modal dialog before git push
   - Show AI analysis and recommendations

### Quick Extension Template:

**package.json:**
```json
{
  "name": "impactguard",
  "displayName": "ImpactGuard",
  "description": "AI-powered code impact analysis",
  "version": "1.0.0",
  "engines": {
    "vscode": "^1.80.0"
  },
  "activationEvents": [
    "onCommand:impactguard.analyze"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "impactguard.analyze",
        "title": "ImpactGuard: Analyze Changes"
      }
    ]
  }
}
```

**src/extension.ts:**
```typescript
import * as vscode from 'vscode';
import axios from 'axios';

export function activate(context: vscode.ExtensionContext) {
    let disposable = vscode.commands.registerCommand(
        'impactguard.analyze',
        async () => {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder open');
                return;
            }

            // Get changed files from git
            const terminal = vscode.window.createTerminal('ImpactGuard');
            terminal.sendText('git diff --name-only HEAD');
            
            // Call ImpactGuard API
            try {
                const response = await axios.post('http://localhost:8000/llm/explain-risk', {
                    repository_path: workspaceFolder.uri.fsPath,
                    file_paths: ['main.py'], // Get from git diff
                    include_code: true
                });

                // Show results
                const panel = vscode.window.createWebviewPanel(
                    'impactguard',
                    'ImpactGuard Analysis',
                    vscode.ViewColumn.Two,
                    {}
                );

                panel.webview.html = getWebviewContent(response.data);
            } catch (error) {
                vscode.window.showErrorMessage(`ImpactGuard error: ${error}`);
            }
        }
    );

    context.subscriptions.push(disposable);
}

function getWebviewContent(data: any): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .risk-high { color: #d73a49; }
                .risk-medium { color: #f9c513; }
                .risk-low { color: #28a745; }
            </style>
        </head>
        <body>
            <h1>ImpactGuard Analysis</h1>
            <h2 class="risk-${data.risk_level.toLowerCase()}">
                Risk: ${data.risk_level}
            </h2>
            <p>${data.explanation}</p>
        </body>
        </html>
    `;
}
```

## 🔧 Configuration

### Workspace Settings

Add to `.vscode/settings.json`:

```json
{
  "impactguard.apiUrl": "http://localhost:8000",
  "impactguard.autoAnalyze": true,
  "impactguard.showInlineWarnings": true,
  "impactguard.riskThreshold": "MEDIUM"
}
```

## 📊 Developer Workflow

### Typical Flow:

```
1. Developer codes
   ↓
2. Developer saves file
   ↓
3. [Optional] Auto-analyze on save
   ↓
4. Developer commits changes
   ↓
5. Developer attempts push
   ↓
6. Pre-push hook triggers
   ↓
7. ImpactGuard analyzes
   ↓
8. AI explains risks
   ↓
9. Developer reviews
   ↓
10. Developer decides: Push or Fix
```

## 🎯 Example Scenarios

### Scenario 1: High-Risk Change

```bash
$ git push

🛡️ ImpactGuard: Analyzing changes before push...

🤖 AI Analysis:
"You're modifying the authentication middleware in auth.py. This is 
high risk because:

1. It affects all API endpoints (24 routes depend on it)
2. The session timeout change could cause race conditions
3. Similar changes in commit a82f caused login failures

Recommendations:
- Update session_handler.py line 42 to handle shorter timeouts
- Add integration tests for auth flow
- Consider feature flag for gradual rollout"

📊 Risk Level: HIGH
📈 Risk Score: 0.87

Continue with push? (y/n)
```

### Scenario 2: Safe Change

```bash
$ git push

🛡️ ImpactGuard: Analyzing changes before push...

🤖 AI Analysis:
"You're updating documentation files. This is low risk - no code 
dependencies affected. Good to go!"

📊 Risk Level: LOW
📈 Risk Score: 0.12

Continue with push? (y/n) y
✅ Proceeding with push...
```

## 🚀 Quick Start

### 1. Install Pre-Push Hook:
```bash
curl -o .git/hooks/pre-push https://raw.githubusercontent.com/your-repo/impactguard/main/hooks/pre-push
chmod +x .git/hooks/pre-push
```

### 2. Configure VS Code Tasks:
```bash
mkdir -p .vscode
curl -o .vscode/tasks.json https://raw.githubusercontent.com/your-repo/impactguard/main/.vscode/tasks.json
```

### 3. Start ImpactGuard Server:
```bash
cd /path/to/impactguard
python main.py
```

### 4. Test It:
```bash
# Make a change
echo "test" >> file.py
git add file.py
git commit -m "test"

# Try to push - ImpactGuard will analyze!
git push
```

## 💡 Best Practices

1. **Always Run Server**: Keep ImpactGuard running in background
2. **Review AI Insights**: Don't blindly accept/reject
3. **Configure Thresholds**: Set appropriate risk levels for your team
4. **Team Adoption**: Share hooks with entire team
5. **CI/CD Integration**: Add to pipeline for automated checks

## 🔗 Integration with CI/CD

### GitHub Actions Example:

```yaml
name: ImpactGuard Analysis

on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Start ImpactGuard
        run: |
          docker run -d -p 8000:8000 impactguard/server
          
      - name: Analyze Changes
        run: |
          curl -X POST http://localhost:8000/llm/explain-risk \
            -H "Content-Type: application/json" \
            -d "{\"repository_path\": \".\", \"file_paths\": $(git diff --name-only origin/main | jq -R -s -c 'split(\"\n\")[:-1]')}"
```

## 📚 Additional Resources

- [Git Hooks Documentation](https://git-scm.com/docs/githooks)
- [VS Code Extension API](https://code.visualstudio.com/api)
- [ImpactGuard API Documentation](http://localhost:8000/docs)

---

**Transform your git workflow with AI-powered pre-push analysis!** 🚀