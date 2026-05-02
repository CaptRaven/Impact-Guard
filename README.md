# ImpactGuard 🛡️

An AI-powered code impact analysis system that predicts potential risks before you commit. Now with **Mistral AI LLM** for deep code reasoning and AI pair programming!

## 🚀 Latest: Mistral AI LLM Integration

ImpactGuard has evolved from a code scanner into an **AI Pair Programming Assistant**!

### 🤖 What's New with Mistral AI:
- 🧠 **Deep "Why" Analysis**: Understand the root cause of risks, not just what they are
- 💬 **Conversational Summaries**: Human-like explanations instead of JSON dumps
- 🔮 **"What If" Scenarios**: Ask hypothetical questions and get detailed predictions
- 🔧 **Actionable Code Fixes**: Get specific line-by-line remediation suggestions
- 💡 **AI Chat Assistant**: Ask questions about your code in natural language

[See Mistral AI Guide →](MISTRAL_AI_GUIDE.md)

### 🎯 IBM WatsonX Integration

Full conversational AI capabilities with voice interaction:

- 🗣️ **Natural Language Queries**: "Analyze my auth changes" or "What's the risk?"
- 🎤 **Voice Input**: Speak your queries instead of typing
- 🔊 **Voice Output**: Get spoken responses with high-quality AI voices
- 💬 **Multi-turn Conversations**: Context-aware dialogue

[See WatsonX Integration Guide →](WATSONX_INTEGRATION.md)

## Features

### 1. Change Impact Analyzer
- Analyzes git diff or modified files
- Identifies dependencies across the repository
- Determines which modules, services, or flows are affected
- Outputs structured impact reports

### 2. Risk Scoring Engine
- Assigns risk scores (Low, Medium, High)
- Considers multiple factors:
  - Critical files (auth, payments, core services)
  - Number of dependent modules affected
  - Frequency of past changes
  - Historical issues or bugs

### 3. Historical Insight Extraction
- Analyzes git history and PRs
- Detects patterns:
  - Files frequently causing bugs
  - High-change areas ("hot zones")
  - Co-change patterns
- Provides warnings about similar past issues

### 4. Smart Reviewer Suggestion
- Uses git blame and commit history
- Identifies top contributors for affected files
- Recommends reviewers with confidence scores

### 5. Guided Learning Path
- For high-risk changes, suggests 3-5 files to understand
- Provides brief explanations for each file
- Prioritizes critical dependencies

### 6. Voice Output (Optional)
- Converts impact reports to spoken explanations
- Concise summaries under 30 seconds
- Clear, confident, technical tone

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd "Impact Guard"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file (optional):
```bash
cp .env.example .env
```

## Usage

### Starting the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

#### 1. Analyze Changes
```bash
POST /analyze
```

Request body:
```json
{
  "repository_path": "/path/to/repo",
  "changed_files": [
    {
      "path": "src/auth.ts",
      "additions": 50,
      "deletions": 10
    }
  ],
  "branch": "main"
}
```

#### 2. Analyze Specific Files
```bash
POST /analyze/files
```

Request body:
```json
{
  "repository_path": "/path/to/repo",
  "file_paths": ["src/auth.ts", "src/payment.ts"]
}
```

#### 3. Analyze Uncommitted Changes
```bash
POST /analyze/diff
```

Request body:
```json
{
  "repository_path": "/path/to/repo",
  "branch": "main"
}
```

#### 4. Get Quick Summary
```bash
POST /summary
```

Request body:
```json
{
  "repository_path": "/path/to/repo",
  "file_paths": ["src/auth.ts"]
}
```

#### 5. Get Voice Summary
```bash
POST /voice
```

Request body:
```json
{
  "repository_path": "/path/to/repo",
  "file_paths": ["src/auth.ts"]
}
```

### Example Response

```json
{
  "risk_level": "HIGH",
  "risk_score": 0.87,
  "affected_areas": ["authentication", "payment_service"],
  "critical_files": ["auth.ts", "paymentProcessor.ts"],
  "warnings": [
    {
      "message": "Similar change caused login failure in commit a82f",
      "severity": "high",
      "related_files": ["auth.ts"]
    },
    {
      "message": "High dependency impact across 3 services",
      "severity": "high"
    }
  ],
  "suggested_reviewers": [
    {
      "name": "Sarah",
      "email": "sarah@example.com",
      "confidence": 0.87,
      "commits_count": 45,
      "expertise_areas": ["authentication", "api"]
    },
    {
      "name": "Mike",
      "email": "mike@example.com",
      "confidence": 0.65,
      "commits_count": 23,
      "expertise_areas": ["payments"]
    }
  ],
  "learning_path": [
    {
      "file": "auth.ts",
      "reason": "Core authentication logic",
      "importance": "high",
      "lines_of_code": 250
    },
    {
      "file": "middleware.ts",
      "reason": "Handles request validation",
      "importance": "medium",
      "lines_of_code": 150
    }
  ],
  "metadata": {
    "total_changes": 60,
    "files_count": 2
  },
  "voice_summary": "High risk detected with score 0.87. Affected areas: authentication, payment service. 2 critical files affected. Warning: Similar change caused login failure in commit a82f. Recommended reviewer: Sarah. Thorough review and testing required before proceeding."
}
```

## Python Usage

You can also use ImpactGuard directly in Python:

```python
from services import ImpactService
from models import ChangeInput, FileChange

# Initialize service
service = ImpactService("/path/to/repo")

# Analyze specific files
report = service.analyze_specific_files([
    "src/auth.ts",
    "src/payment.ts"
])

# Print summary
print(service.get_quick_summary(report))

# Get voice summary
voice_summary = service.voice_service.generate_voice_summary(report)
print(voice_summary)
```

## Configuration

Edit `config.py` to customize:

- Risk thresholds
- Critical file patterns
- Analysis depth
- Reviewer suggestion limits
- Voice output settings

## Architecture

```
ImpactGuard/
├── analyzers/              # Core analysis modules
│   ├── change_analyzer.py  # Change impact analysis
│   ├── risk_scorer.py      # Risk scoring engine
│   ├── history_analyzer.py # Historical insights
│   ├── reviewer_suggester.py # Reviewer suggestions
│   └── learning_path_generator.py # Learning paths
├── services/               # Service layer
│   ├── impact_service.py   # Main orchestrator
│   └── voice_service.py    # Voice output
├── models.py               # Data models
├── config.py               # Configuration
├── main.py                 # FastAPI application
└── requirements.txt        # Dependencies
```

## Requirements

- Python 3.8+
- Git repository with commit history
- Dependencies listed in requirements.txt

## Limitations

- Requires a valid git repository
- Analysis accuracy depends on commit history quality
- Voice output requires system TTS support
- Best suited for repositories with consistent commit practices

## Future Enhancements

- Machine learning for better risk prediction
- Integration with CI/CD pipelines
- Support for multiple VCS systems
- Real-time analysis during development
- Team collaboration features
- Custom rule definitions

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.