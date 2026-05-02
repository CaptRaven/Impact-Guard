# WatsonX Integration Guide

ImpactGuard now includes full IBM WatsonX integration for AI-powered conversational code analysis!

## Overview

The WatsonX integration adds three powerful AI capabilities:

1. **WatsonX NLU (Natural Language Understanding)** - Understand natural language queries
2. **WatsonX TTS (Text-to-Speech)** - High-quality voice responses
3. **WatsonX STT (Speech-to-Text)** - Voice input support

## Features

### 🗣️ Natural Language Queries
Ask questions in plain English:
- "Analyze my authentication changes"
- "What's the risk of modifying payment.py?"
- "Who should review my database changes?"
- "Show me files I need to understand before editing auth"

### 🎤 Voice Input
Speak your queries instead of typing them!

### 🔊 Voice Output
Get spoken responses with high-quality AI voices

### 💬 Conversational Interface
Multi-turn conversations with context awareness

## Setup

### 1. Get IBM WatsonX Credentials

Visit [IBM Cloud](https://cloud.ibm.com/) and create:
- Natural Language Understanding service
- Text to Speech service
- Speech to Text service

### 2. Configure Credentials

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
# WatsonX NLU (Natural Language Understanding)
WATSONX_NLU_API_KEY=your_nlu_api_key_here
WATSONX_NLU_URL=https://api.us-south.natural-language-understanding.watson.cloud.ibm.com
WATSONX_NLU_VERSION=2022-04-07

# WatsonX TTS (Text-to-Speech)
WATSONX_TTS_API_KEY=your_tts_api_key_here
WATSONX_TTS_URL=https://api.us-south.text-to-speech.watson.cloud.ibm.com
WATSONX_TTS_VOICE=en-US_AllisonV3Voice

# WatsonX STT (Speech-to-Text)
WATSONX_STT_API_KEY=your_stt_api_key_here
WATSONX_STT_URL=https://api.us-south.speech-to-text.watson.cloud.ibm.com
WATSONX_STT_MODEL=en-US_BroadbandModel
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Server

```bash
python main.py
```

## API Endpoints

### Conversational Query (Text)

```bash
POST /conversation/query
```

**Request:**
```json
{
  "query": "analyze my auth changes",
  "repository_path": "/path/to/repo"
}
```

**Response:**
```json
{
  "query": "analyze my auth changes",
  "parsed_query": {
    "intent": "analyze",
    "files": ["auth.py"],
    "areas": ["auth"],
    "confidence": 0.9
  },
  "analysis": {
    "risk_level": "MEDIUM",
    "risk_score": 0.65,
    ...
  },
  "response_text": "Medium risk detected with score 0.65. Affected areas: authentication...",
  "has_voice": true,
  "conversation_id": 1
}
```

### Voice Query

```bash
POST /conversation/voice-query
```

**Request:**
- Form data with audio file
- Optional repository_path

**Response:**
```json
{
  "transcript": "analyze my authentication changes",
  "query": "analyze my authentication changes",
  "analysis": {...},
  "response_text": "...",
  "input_type": "voice"
}
```

### Get Voice Response

```bash
POST /conversation/voice-response
```

**Request:**
```json
{
  "text": "High risk detected in authentication module"
}
```

**Response:**
- Audio file (WAV format)

### Conversation History

```bash
GET /conversation/history?limit=10
```

**Response:**
```json
{
  "history": [
    {
      "query": "analyze auth.py",
      "parsed": {...},
      "response": "..."
    }
  ],
  "count": 1
}
```

### Set Default Repository

```bash
POST /conversation/set-repository
```

**Request:**
```json
{
  "repository_path": "/path/to/repo"
}
```

### Clear History

```bash
DELETE /conversation/history
```

### Conversation Summary

```bash
GET /conversation/summary
```

**Response:**
```json
{
  "total_queries": 5,
  "nlu_available": true,
  "tts_available": true,
  "stt_available": true,
  "default_repo": "/path/to/repo"
}
```

## Usage Examples

### Example 1: Text Query

```python
import requests

response = requests.post(
    "http://localhost:8000/conversation/query",
    json={
        "query": "What's the risk of changing payment.py?",
        "repository_path": "/path/to/repo"
    }
)

result = response.json()
print(f"Risk: {result['analysis']['risk_level']}")
print(f"Response: {result['response_text']}")
```

### Example 2: Voice Query

```python
import requests

with open("query.wav", "rb") as audio_file:
    response = requests.post(
        "http://localhost:8000/conversation/voice-query",
        files={"audio": audio_file},
        data={"repository_path": "/path/to/repo"}
    )

result = response.json()
print(f"You said: {result['transcript']}")
print(f"Analysis: {result['response_text']}")
```

### Example 3: Get Voice Response

```python
import requests

response = requests.post(
    "http://localhost:8000/conversation/voice-response",
    json={"text": "High risk detected in authentication module"}
)

# Save audio file
with open("response.wav", "wb") as f:
    f.write(response.content)

print("Voice response saved to response.wav")
```

### Example 4: Conversational Flow

```python
import requests

base_url = "http://localhost:8000"

# Set default repository
requests.post(
    f"{base_url}/conversation/set-repository",
    json={"repository_path": "/path/to/repo"}
)

# First query
response1 = requests.post(
    f"{base_url}/conversation/query",
    json={"query": "analyze auth.py"}
)
print(response1.json()['response_text'])

# Follow-up query (uses context)
response2 = requests.post(
    f"{base_url}/conversation/query",
    json={"query": "who should review it?"}
)
print(response2.json()['response_text'])

# Get history
history = requests.get(f"{base_url}/conversation/history")
print(f"Total conversations: {history.json()['count']}")
```

## Natural Language Query Examples

### Risk Assessment
- "Is it safe to modify auth.py?"
- "What's the risk level for payment changes?"
- "How dangerous is editing database.py?"

### Reviewer Suggestions
- "Who should review my auth changes?"
- "Recommend reviewers for payment.py"
- "Who's the expert on database code?"

### Learning Path
- "What should I read before editing auth?"
- "Show me files to understand for payment changes"
- "What do I need to know about the database module?"

### Historical Analysis
- "Has auth.py caused issues before?"
- "Show me the history of payment.py"
- "What are the hot zones in this repo?"

### Quick Summary
- "Give me a quick summary of my changes"
- "Brief overview of auth.py impact"
- "Summarize the risk"

## Voice Configuration

### Available Voices (TTS)

English voices:
- `en-US_AllisonV3Voice` (default, female)
- `en-US_LisaV3Voice` (female)
- `en-US_MichaelV3Voice` (male)
- `en-GB_KateV3Voice` (British, female)

Change voice in `.env`:
```bash
WATSONX_TTS_VOICE=en-US_MichaelV3Voice
```

### Audio Formats (STT)

Supported input formats:
- WAV (recommended)
- MP3
- FLAC
- OGG
- WebM

## Python SDK Usage

```python
from services import ConversationalService

# Initialize service
conv_service = ConversationalService(
    default_repo_path="/path/to/repo"
)

# Text query
result = conv_service.process_text_query(
    "analyze my auth changes"
)
print(result['response_text'])

# Voice query
result = conv_service.process_voice_query(
    "query.wav",
    repo_path="/path/to/repo"
)
print(f"Transcript: {result['transcript']}")
print(f"Response: {result['response_text']}")

# Generate voice response
audio_data = conv_service.get_voice_response(
    "High risk detected",
    output_path="response.wav"
)

# Get conversation history
history = conv_service.get_conversation_history(limit=5)
print(f"Recent conversations: {len(history)}")
```

## Advanced Features

### Intent Recognition

The NLU service automatically detects intent:
- `analyze` - General analysis
- `assess_risk` - Risk assessment
- `suggest_reviewers` - Reviewer suggestions
- `learning_path` - Learning recommendations
- `historical_analysis` - Historical insights
- `quick_summary` - Brief summary

### Context Awareness

The system maintains conversation context:
```python
# First query
"analyze auth.py"

# Follow-up (uses context from first query)
"who should review it?"  # "it" refers to auth.py
"what's the risk?"       # risk of auth.py changes
```

### Entity Extraction

Automatically extracts:
- File paths
- Module names
- Areas/components
- Repository paths

## Troubleshooting

### NLU Not Working
- Check API key and URL in `.env`
- Verify service is active in IBM Cloud
- Check network connectivity

### TTS Not Working
- Verify TTS credentials
- Check voice name is valid
- Ensure output path is writable

### STT Not Working
- Check audio file format
- Verify file size < 100MB
- Ensure audio is clear and in English

### No Voice Response
- Check `VOICE_ENABLED=true` in `.env`
- Verify TTS credentials
- Check system audio output

## Performance Tips

1. **Batch Queries**: Process multiple files in one query
2. **Set Default Repo**: Avoid repeating repository path
3. **Use Context**: Follow-up queries are faster
4. **Cache Results**: Store analysis results for reuse

## Security Notes

- Never commit `.env` file with credentials
- Use environment variables in production
- Rotate API keys regularly
- Limit API access to trusted networks

## Cost Optimization

- NLU: ~$0.003 per query
- TTS: ~$0.02 per 1000 characters
- STT: ~$0.02 per minute

Tips:
- Use rule-based parsing when possible (fallback)
- Cache voice responses
- Limit conversation history size

## Support

For issues or questions:
- Check IBM WatsonX documentation
- Review API logs
- Test with curl/Postman first
- Verify credentials are correct

## Next Steps

1. Configure your WatsonX credentials
2. Test with simple queries
3. Try voice input/output
4. Integrate into your workflow
5. Customize for your team

Happy analyzing! 🚀