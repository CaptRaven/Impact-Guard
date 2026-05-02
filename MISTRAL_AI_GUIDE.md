# 🤖 Mistral AI LLM Integration Guide

## Overview

ImpactGuard now includes **Mistral AI LLM** integration, transforming it from a code analysis tool into an **AI Pair Programming Assistant**. This guide explains how to set up and use the advanced AI features.

## 🎯 What Mistral AI Adds

### 1. **Deep "Why" Analysis**
Instead of just telling you "HIGH RISK", Mistral explains:
- **Root cause** of the risk
- **What could go wrong** in production
- **Why this specific combination** is dangerous
- **What developers often forget** in similar changes

**Example:**
```
Standard: "HIGH RISK - 24 files depend on config.py"

With Mistral: "Changing this timeout in config.py is high risk because 
it will likely cause race conditions in the database migration service. 
The migration handler expects a 30-second timeout, but your change 
reduces it to 10 seconds, which isn't enough for large table operations."
```

### 2. **Conversational Summaries**
Get human-like explanations instead of JSON dumps:

**Example:**
```
"Hey, I noticed you're touching the auth logic. Usually when we do this, 
we forget to update the session handler in main.py. Do you want me to 
check that for you?"
```

### 3. **Complex "What If" Scenarios**
Ask hypothetical questions and get detailed predictions:

**Example Query:**
```
"If I refactor the database schema today, which part of the front-end 
will break first?"
```

**Mistral Response:**
```
"The user profile component will break first because it directly queries 
the 'users' table. Here's the cascade:
1. ProfileView.tsx (line 42) - Expects 'email' field
2. UserSettings.tsx (line 89) - Depends on 'preferences' JSON
3. Dashboard.tsx (line 156) - Aggregates user stats

Recommended order: Update ProfileView first, then test UserSettings..."
```

### 4. **Actionable Code Fixes**
Get specific code changes to mitigate risks:

**Example:**
```json
{
  "auth.py": [
    {
      "line": 42,
      "suggestion": "Add null check before accessing user.session",
      "reason": "Prevents race condition when session expires during request"
    }
  ]
}
```

## 🚀 Setup Instructions

### Step 1: Get Mistral AI API Key

1. Go to [Mistral AI Console](https://console.mistral.ai/)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create New Key**
5. Copy your API key

**Free Tier Available:** Mistral offers a generous free tier for testing!

### Step 2: Configure Environment

Add to your `.env` file:

```bash
# Mistral AI Configuration
MISTRAL_API_KEY=your_actual_api_key_here

# Optional: Override defaults
MISTRAL_MODEL=mistral-large-latest
MISTRAL_TEMPERATURE=0.4
```

### Step 3: Install Dependencies

```bash
# Activate conda environment
conda activate impactguard

# Install Mistral AI SDK
pip install mistralai

# Or reinstall all requirements
pip install -r requirements.txt
```

### Step 4: Restart Server

```bash
python main.py
```

You should see:
```
✅ Mistral AI LLM initialized successfully
```

## 📚 API Endpoints

### 1. Explain Risk Reasoning

**Endpoint:** `POST /llm/explain-risk`

Get deep "why" explanation of risks.

**Request:**
```json
{
  "repository_path": "/path/to/repo",
  "file_paths": ["config.py", "auth.py"],
  "include_code": true
}
```

**Response:**
```json
{
  "explanation": "Detailed explanation of WHY the change is risky...",
  "risk_level": "HIGH",
  "risk_score": 0.87,
  "llm_enabled": true
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/llm/explain-risk \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "/Users/mac/Documents/Impact Guard",
    "file_paths": ["main.py", "config.py"],
    "include_code": true
  }'
```

### 2. Conversational Summary

**Endpoint:** `POST /llm/conversational-summary`

Get human-like, conversational summary.

**Request:**
```json
{
  "repository_path": "/path/to/repo",
  "file_paths": ["main.py"],
  "user_context": "I'm adding a new authentication method"
}
```

**Response:**
```json
{
  "summary": "Hey, I see you're adding auth logic...",
  "risk_level": "MEDIUM",
  "risk_score": 0.65,
  "llm_enabled": true
}
```

### 3. What-If Analysis

**Endpoint:** `POST /llm/what-if`

Analyze hypothetical scenarios.

**Request:**
```json
{
  "scenario": "If I refactor the database schema, what will break?",
  "repository_path": "/path/to/repo",
  "include_code": true
}
```

**Response:**
```json
{
  "analysis": "Detailed prediction of impacts...",
  "scenario": "If I refactor the database schema...",
  "llm_enabled": true
}
```

### 4. Suggest Code Fixes

**Endpoint:** `POST /llm/suggest-fixes`

Get actionable remediation suggestions.

**Request:**
```json
{
  "repository_path": "/path/to/repo",
  "file_paths": ["auth.py", "models.py"]
}
```

**Response:**
```json
{
  "suggestions": {
    "auth.py": [
      {
        "line": 42,
        "suggestion": "Add null check",
        "reason": "Prevents race condition"
      }
    ]
  },
  "risk_level": "HIGH",
  "llm_enabled": true
}
```

### 5. General Chat

**Endpoint:** `POST /llm/chat`

Chat with AI about your code.

**Request:**
```json
{
  "message": "How should I safely update the authentication system?",
  "repository_path": "/path/to/repo",
  "conversation_history": [
    {"role": "user", "content": "Previous question..."},
    {"role": "assistant", "content": "Previous answer..."}
  ]
}
```

**Response:**
```json
{
  "response": "To safely update authentication...",
  "llm_enabled": true
}
```

## 🎨 Using in the Demo UI

### Access LLM Features

1. Open http://localhost:8000
2. Navigate to **🤖 AI Features** tab
3. You'll see new LLM-powered sections

### New UI Features

#### 1. **Deep Risk Explanation**
- Enter file paths
- Click "Explain Why This Is Risky"
- Get detailed reasoning

#### 2. **AI Chat Assistant**
- Ask questions in natural language
- Get context-aware responses
- Maintain conversation history

#### 3. **What-If Simulator**
- Type hypothetical scenarios
- Get predicted impacts
- See cascade effects

#### 4. **Code Fix Suggestions**
- Analyze risky changes
- Get specific line-by-line fixes
- Understand the reasoning

## 💡 Best Practices

### 1. **Include Code Context**
Set `include_code: true` for deeper analysis:
```json
{
  "include_code": true  // Sends actual code to LLM
}
```

### 2. **Provide User Context**
Help the AI understand your intent:
```json
{
  "user_context": "I'm refactoring for performance"
}
```

### 3. **Use Conversation History**
Maintain context across multiple questions:
```json
{
  "conversation_history": [
    {"role": "user", "content": "What's risky about this?"},
    {"role": "assistant", "content": "The main risk is..."}
  ]
}
```

### 4. **Limit File Count**
For better performance, analyze 5-10 files at a time.

## 🔧 Configuration Options

### Model Selection

Choose the best model for your needs:

```bash
# Best for code reasoning (default)
MISTRAL_MODEL=mistral-large-latest

# Faster, cheaper (good for simple queries)
MISTRAL_MODEL=mistral-medium-latest

# Smallest, fastest (basic analysis)
MISTRAL_MODEL=mistral-small-latest
```

### Temperature Control

Adjust creativity vs. precision:

```bash
# More precise, technical (default)
MISTRAL_TEMPERATURE=0.3

# Balanced
MISTRAL_TEMPERATURE=0.5

# More creative, conversational
MISTRAL_TEMPERATURE=0.7
```

## 📊 Comparison: With vs Without LLM

| Feature | Without LLM | With Mistral AI |
|---------|-------------|-----------------|
| **Risk Detection** | ✅ Identifies risks | ✅ Explains WHY risky |
| **Summaries** | 📋 Structured JSON | 💬 Conversational |
| **What-If** | ❌ Not available | ✅ Deep reasoning |
| **Code Fixes** | 📚 Learning path | 🔧 Specific changes |
| **Chat** | ❌ Not available | ✅ Full conversation |
| **Speed** | ⚡ Instant | 🐢 2-5 seconds |
| **Cost** | 💰 Free | 💰 API costs |

## 🎯 Use Cases

### 1. **Pre-Commit Review**
```bash
# Before committing
curl -X POST http://localhost:8000/llm/explain-risk \
  -d '{"repository_path": ".", "file_paths": ["changed_file.py"]}'
```

### 2. **Refactoring Planning**
```bash
# Plan major changes
curl -X POST http://localhost:8000/llm/what-if \
  -d '{"scenario": "If I split this monolith into microservices..."}'
```

### 3. **Learning & Mentorship**
```bash
# Ask questions
curl -X POST http://localhost:8000/llm/chat \
  -d '{"message": "Why is this pattern considered bad practice?"}'
```

### 4. **Code Review Assistance**
```bash
# Get fix suggestions
curl -X POST http://localhost:8000/llm/suggest-fixes \
  -d '{"repository_path": ".", "file_paths": ["pr_files.py"]}'
```

## 🔒 Privacy & Security

### Data Handling
- Code is sent to Mistral AI servers for analysis
- Mistral AI does NOT store your code permanently
- API calls are encrypted (HTTPS)

### Best Practices
1. **Don't include secrets** in analyzed code
2. **Review sensitive code** before analysis
3. **Use environment variables** for credentials
4. **Consider self-hosted** for highly sensitive projects

### Fallback Mode
If Mistral AI is unavailable:
- Core features still work
- Basic explanations provided
- No API calls made

## 🐛 Troubleshooting

### Issue: "Mistral AI not initialized"

**Solution:**
```bash
# Check API key
echo $MISTRAL_API_KEY

# Verify in .env file
cat .env | grep MISTRAL

# Restart server
python main.py
```

### Issue: "Rate limit exceeded"

**Solution:**
- Wait a few minutes
- Upgrade Mistral AI plan
- Reduce request frequency

### Issue: "Slow responses"

**Solution:**
```bash
# Use smaller model
MISTRAL_MODEL=mistral-medium-latest

# Reduce code context
"include_code": false

# Limit file count
"file_paths": ["main.py"]  # Not 20 files
```

## 📈 Performance Tips

1. **Cache Results:** Store LLM responses for repeated queries
2. **Batch Requests:** Analyze multiple files in one request
3. **Use Smaller Models:** For simple queries
4. **Limit Context:** Only include relevant code
5. **Async Processing:** Don't block on LLM calls

## 🎓 Learning Resources

- [Mistral AI Documentation](https://docs.mistral.ai/)
- [Mistral AI Models](https://docs.mistral.ai/platform/endpoints/)
- [Best Practices](https://docs.mistral.ai/guides/prompting/)

## 🚀 Next Steps

1. ✅ Get Mistral API key
2. ✅ Configure `.env` file
3. ✅ Install dependencies
4. ✅ Restart server
5. 🎯 Try the demo UI
6. 📚 Read API documentation
7. 🔧 Integrate into workflow

---

**Transform ImpactGuard from a scanner into your AI pair programmer!** 🤖✨