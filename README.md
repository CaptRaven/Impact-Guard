# ImpactGuard 🛡️

**AI-Powered Code Impact Analysis** - Analyze code changes BEFORE you commit and prevent production issues.

> **Live Git Monitoring** • **Mistral AI Brain** • **VS Code Integration** • **Real-time Analysis**

---

## 🎯 What is ImpactGuard?

ImpactGuard is an intelligent code analysis system that watches your repository in real-time and provides AI-powered insights before you push code. Think of it as having a senior developer reviewing every change instantly.

### ⚡ Key Features

- 🔴 **Live Git Monitoring** - Detects staged, unstaged, and untracked files in real-time
- 🤖 **Bob - AI Analyzer** - Mistral AI-powered analysis with 5 clear insights
- 🎨 **VS Code UI** - Professional interface with Lucide icons
- 🔌 **Git Hook Integration** - Automatic analysis before every push
- 📊 **Real-time Status** - Live file counter in status bar
- 🗣️ **Voice AI** - IBM WatsonX for conversational interaction

---

## 🤖 Meet Bob - Your AI Code Analyzer

Bob analyzes your changes and gives you **exactly 5 things**:

### 1. 🔥 Impact Prediction
"This change affects authentication → session management → 3 downstream services → HIGH risk"

### 2. 🔥 Breakage Simulation
"Similar change in commit #a82f caused login failures lasting 3 hours"

### 3. 🔥 Smart Reviewer Assignment
"Send this to Sarah Chen (87% ownership of authentication module)"

### 4. 🔥 Auto Learning Path
"Before editing, understand: 1. auth.py 2. session_handler.py 3. middleware.py"
*(Only shown for HIGH risk changes)*

### 5. 🔥 Voice Explanation
"You're reducing timeout from 30 to 10 seconds. Risky because migrations take 15-25 seconds..."

[See Bob in Action →](MISTRAL_AI_GUIDE.md)

---

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies
```bash
# Clone repository
git clone <repository-url>
cd "Impact Guard"

# Setup conda environment
conda create -n impactguard python=3.10
conda activate impactguard

# Install packages
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional but Recommended)
```bash
# Copy example config
cp .env.example .env

# Add your Mistral AI key for Bob
echo "MISTRAL_API_KEY=your_key_here" >> .env
```

Get your free Mistral AI key: https://console.mistral.ai/

### 3. Start & Use
```bash
# Start the server
python main.py

# In another terminal, install git hook
./install_hook.sh

# Make changes and push - Bob analyzes automatically!
git push
```

---

## 🎨 User Interface

### Demo UI
Open http://localhost:8000 for a beautiful VS Code-inspired interface:

- **Live Git Monitoring** - See changed files in real-time
- **Interactive Analysis** - Click to analyze any file
- **Status Bar Counter** - Shows live file count
- **Lucide Icons** - Professional, scalable icons
- **4 Tabs**: Analyze Files, Quick Summary, AI Features, System Health

### Git Hook Integration
Every time you `git push`, Bob automatically analyzes:

```bash
$ git push

🛡️  ImpactGuard: Analyzing changes before push...
📁 Analyzing 2 changed file(s)...
🤖 Bob is analyzing your changes...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 RISK LEVEL: HIGH (Score: 0.87)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 BOB'S ANALYSIS (AI-Powered)

🔥 1. IMPACT PREDICTION
This change affects authentication → 3 services → HIGH risk

🔥 2. BREAKAGE SIMULATION
Similar change in commit #a82f caused login failures

🔥 3. SMART REVIEWER ASSIGNMENT
Send this to Sarah (87% ownership of auth module)

🔥 4. AUTO LEARNING PATH
Before editing: 1. auth.py 2. session_handler.py

🔥 5. VOICE EXPLANATION
Timeout reduction risky - migrations need 15-25 seconds...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  HIGH RISK detected! Are you sure you want to push?
Continue with push? (y/n)
```

---

## 📡 API Endpoints

### Core Analysis

#### Bob Analyzer (Main Endpoint)
```bash
POST /bob/analyze
```
Returns Bob's 5-section analysis

**Request:**
```json
{
  "repository_path": "/path/to/repo",
  "changed_files": ["auth.py", "session.py"]
}
```

**Response:**
```json
{
  "success": true,
  "bob_enabled": true,
  "analysis": {
    "impact_prediction": "This change affects auth → 3 services → HIGH risk",
    "breakage_simulation": "Similar change in #a82f caused failures",
    "smart_reviewer": "Send to Sarah (87% ownership)",
    "learning_path": "Understand: 1. auth.py 2. session.py",
    "voice_explanation": "Timeout too short for migrations..."
  },
  "risk_level": "HIGH",
  "risk_score": 0.87
}
```

#### Standard Analysis
```bash
POST /analyze/files      # Analyze specific files
POST /analyze/diff       # Analyze git diff
POST /summary            # Quick text summary
POST /voice              # Voice summary
```

### Mistral AI LLM Endpoints
```bash
POST /llm/explain-risk          # Deep "why" explanation
POST /llm/conversational-summary # Human-like summary
POST /llm/what-if               # Hypothetical scenarios
POST /llm/suggest-fixes         # Code remediation
POST /llm/chat                  # General AI chat
```

### WatsonX Voice AI
```bash
POST /conversational/query      # Natural language query
POST /conversational/speak      # Text-to-speech
POST /conversational/transcribe # Speech-to-text
POST /conversational/voice-query # Full voice interaction
```

### System
```bash
GET  /                  # Demo UI
GET  /api              # API information
GET  /health           # System health
GET  /docs             # Swagger documentation
```

---

## 🏗️ Architecture

### Core Components

```
ImpactGuard/
├── analyzers/                    # Analysis engines
│   ├── change_analyzer.py        # Live git monitoring (268 lines)
│   ├── risk_scorer.py            # Multi-factor risk scoring (226 lines)
│   ├── history_analyzer.py       # Pattern detection (343 lines)
│   ├── reviewer_suggester.py     # Expert identification (235 lines)
│   └── learning_path_generator.py # Guided learning (262 lines)
│
├── services/                     # AI services
│   ├── bob_analyzer.py           # Main AI brain (232 lines) ⭐
│   ├── mistral_llm_service.py    # Deep reasoning (485 lines)
│   ├── unified_llm_service.py    # Comprehensive analysis (298 lines)
│   ├── watsonx_nlu_service.py    # Natural language (310 lines)
│   ├── watsonx_tts_service.py    # Text-to-speech (226 lines)
│   ├── watsonx_stt_service.py    # Speech-to-text (276 lines)
│   ├── conversational_service.py # Voice orchestration (253 lines)
│   ├── impact_service.py         # Main orchestrator (180 lines)
│   └── voice_service.py          # Fallback TTS (125 lines)
│
├── static/
│   └── index.html                # VS Code-style UI
│
├── hooks/
│   └── pre-push                  # Git hook script
│
├── main.py                       # FastAPI server (900+ lines)
├── models.py                     # Data models (96 lines)
├── config.py                     # Configuration (79 lines)
└── requirements.txt              # Dependencies
```

### How It Works

```
Developer makes changes
        ↓
Git detects changes (live monitoring)
        ↓
Status bar updates (real-time counter)
        ↓
Developer attempts push
        ↓
Pre-push hook triggers
        ↓
Calls /bob/analyze endpoint
        ↓
Backend analyzes:
  • Reads actual code
  • Checks git history
  • Calculates dependencies
  • Identifies reviewers
        ↓
Sends to Mistral AI LLM
        ↓
LLM provides deep reasoning
        ↓
Returns 5 clear sections
        ↓
Hook displays beautifully
        ↓
Developer decides: Push or Fix
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Mistral AI (Recommended for Bob)
MISTRAL_API_KEY=your_mistral_key
MISTRAL_MODEL=mistral-large-latest
MISTRAL_TEMPERATURE=0.4

# IBM WatsonX (Optional - for voice features)
WATSONX_NLU_API_KEY=your_nlu_key
WATSONX_NLU_URL=https://api.us-south.natural-language-understanding.watson.cloud.ibm.com

WATSONX_TTS_API_KEY=your_tts_key
WATSONX_TTS_URL=https://api.us-south.text-to-speech.watson.cloud.ibm.com

WATSONX_STT_API_KEY=your_stt_key
WATSONX_STT_URL=https://api.us-south.speech-to-text.watson.cloud.ibm.com
```

### Git Hook Configuration

```bash
# Customize hook behavior
export IMPACTGUARD_URL=http://localhost:8000
export IMPACTGUARD_ENABLED=true
```

---

## 📚 Documentation

### Guides
- [**QUICKSTART.md**](QUICKSTART.md) - 5-minute setup guide
- [**MISTRAL_AI_GUIDE.md**](MISTRAL_AI_GUIDE.md) - Bob & LLM features
- [**WATSONX_INTEGRATION.md**](WATSONX_INTEGRATION.md) - Voice AI setup
- [**VSCODE_EXTENSION_GUIDE.md**](VSCODE_EXTENSION_GUIDE.md) - Git integration
- [**DEMO_UI_GUIDE.md**](DEMO_UI_GUIDE.md) - UI usage guide

### Setup & Troubleshooting
- [**SETUP_INSTRUCTIONS.md**](SETUP_INSTRUCTIONS.md) - Complete setup
- [**IBM_CREDENTIALS_GUIDE.md**](IBM_CREDENTIALS_GUIDE.md) - Get API keys
- [**INSTALLATION_FIX.md**](INSTALLATION_FIX.md) - Common issues
- [**ERROR_CHECK_AND_FIX.md**](ERROR_CHECK_AND_FIX.md) - Error diagnostics

---

## ✨ What Makes ImpactGuard Special

### vs Traditional Tools

| Feature | Traditional Tools | ImpactGuard |
|---------|------------------|-------------|
| **Analysis** | Static, on-demand | Live, real-time |
| **Output** | JSON dumps | 5 clear sections |
| **Insights** | "High risk" | "Why risky + how to fix" |
| **Context** | None | Historical patterns |
| **Reviewers** | Manual | AI-assigned experts |
| **Learning** | None | Guided file paths |
| **Integration** | Manual | Automatic git hooks |
| **UI** | Command line | VS Code-style |

### Key Differentiators

1. **Live Git Monitoring** - Sees changes as you type
2. **Bob's 5 Sections** - Clear, actionable insights
3. **Mistral AI Brain** - Deep reasoning, not just pattern matching
4. **Real-time Status** - Always know what's being analyzed
5. **Professional UI** - Lucide icons, VS Code aesthetic
6. **Git Hook Integration** - Automatic pre-push analysis
7. **Voice Interaction** - Ask questions, get spoken answers

---

## 🎯 Use Cases

### 1. Pre-Commit Safety
Analyze changes before pushing to catch issues early

### 2. Code Review Assistant
Get AI insights for pull requests

### 3. Developer Learning
Understand code dependencies and patterns

### 4. Team Standards
Enforce review practices automatically

### 5. Risk Assessment
Predict production impact before deployment

### 6. Onboarding Tool
Help new developers understand the codebase

---

## 🚀 Advanced Features

### Live Git Detection
- **Staged files**: `git diff --cached`
- **Unstaged files**: `git diff`
- **Untracked files**: `git ls-files --others`
- **Smart deduplication**: No double-counting
- **Automatic path detection**: Works in any directory

### AI-Powered Analysis
- **Mistral AI LLM**: Deep code reasoning
- **Context awareness**: Reads actual code
- **Historical learning**: Learns from past failures
- **Cascade prediction**: Predicts ripple effects
- **Specific recommendations**: Line-by-line fixes

### Voice Interaction
- **Natural language queries**: Ask in plain English
- **Text-to-speech**: Hear the analysis
- **Speech-to-text**: Speak your questions
- **Full conversations**: Multi-turn dialogue

---

## 📊 System Requirements

- **Python**: 3.10+
- **Git**: Any recent version
- **OS**: macOS, Linux, Windows
- **Memory**: 2GB+ recommended
- **API Keys**: Mistral AI (optional but recommended)

---

## 🎓 Getting Help

### Quick Links
- **Demo UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Common Issues

**"Bob not configured"**
```bash
# Add Mistral API key
echo "MISTRAL_API_KEY=your_key" >> .env
# Restart server
python main.py
```

**"Git hook not working"**
```bash
# Reinstall hook
./install_hook.sh
# Make it executable
chmod +x .git/hooks/pre-push
```

**"Server not starting"**
```bash
# Check if port 8000 is available
lsof -i :8000
# Kill existing process if needed
kill -9 <PID>
```

---

## 🌟 What's Working

### Core Features ✅
- ✅ Real-time git monitoring (staged, unstaged, untracked)
- ✅ Dependency analysis
- ✅ Risk scoring (LOW/MEDIUM/HIGH)
- ✅ Historical pattern detection
- ✅ Smart reviewer suggestions
- ✅ Learning path generation

### AI Features ✅
- ✅ Bob's 5-section analysis
- ✅ Mistral AI LLM integration
- ✅ Deep "why" explanations
- ✅ Conversational summaries
- ✅ "What if" scenarios
- ✅ Code remediation suggestions

### Voice Features ✅
- ✅ IBM WatsonX NLU (natural language)
- ✅ IBM WatsonX TTS (text-to-speech)
- ✅ IBM WatsonX STT (speech-to-text)
- ✅ Full voice-to-voice interaction
- ✅ Fallback voice synthesis

### Git Integration ✅
- ✅ Pre-push hook
- ✅ Automatic change detection
- ✅ Live status updates
- ✅ Interactive confirmation
- ✅ Beautiful CLI output

### UI/UX ✅
- ✅ VS Code-inspired design
- ✅ Lucide Icons (professional)
- ✅ Live file counter
- ✅ Real-time updates
- ✅ Interactive analysis display

---

## 🎉 Summary

**ImpactGuard is a complete, production-ready AI-powered code analysis system** that:

1. **Monitors** code changes in real-time
2. **Analyzes** dependencies and risks
3. **Predicts** production impacts
4. **Suggests** expert reviewers
5. **Explains** why changes are risky
6. **Recommends** specific fixes
7. **Integrates** seamlessly with git
8. **Provides** professional VS Code-style UI

**All core features work. AI features enhance the experience but are optional.**

---

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please submit a Pull Request.

---

**Built with ❤️ by developers, for developers**

*Transform your git workflow with AI-powered pre-push analysis!* 🛡️✨