# How to Get Your IBM WatsonX API Keys

This guide will walk you through getting your API credentials from IBM Cloud for all three WatsonX services.

## Prerequisites

- IBM Cloud account (free tier available)
- Access to IBM Cloud dashboard

## Step-by-Step Guide

### 1. Sign In to IBM Cloud

1. Go to [https://cloud.ibm.com/](https://cloud.ibm.com/)
2. Click **Log in** (or **Create an account** if you don't have one)
3. Enter your credentials

### 2. Create Natural Language Understanding (NLU) Service

#### A. Navigate to Catalog
1. From the IBM Cloud dashboard, click **Catalog** in the top menu
2. In the search bar, type "Natural Language Understanding"
3. Click on **Natural Language Understanding**

#### B. Create Service Instance
1. Select your region (e.g., Dallas, London, Frankfurt)
2. Choose a pricing plan:
   - **Lite** (Free): 30,000 NLU items/month
   - **Standard**: Pay as you go
3. Give it a name (e.g., "ImpactGuard-NLU")
4. Click **Create**

#### C. Get API Credentials
1. After creation, you'll be redirected to the service page
2. Click **Manage** in the left sidebar
3. You'll see:
   - **API Key**: Copy this (looks like: `aBcDeFgHiJkLmNoPqRsTuVwXyZ123456789`)
   - **URL**: Copy this (looks like: `https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/xxxxx`)

**Save these credentials!**

```
WATSONX_NLU_API_KEY=your_api_key_here
WATSONX_NLU_URL=your_url_here
```

### 3. Create Text to Speech (TTS) Service

#### A. Navigate to Catalog
1. Click **Catalog** in the top menu
2. Search for "Text to Speech"
3. Click on **Text to Speech**

#### B. Create Service Instance
1. Select your region
2. Choose a pricing plan:
   - **Lite** (Free): 10,000 characters/month
   - **Standard**: Pay as you go
3. Name it (e.g., "ImpactGuard-TTS")
4. Click **Create**

#### C. Get API Credentials
1. Click **Manage** in the left sidebar
2. Copy:
   - **API Key**
   - **URL** (looks like: `https://api.us-south.text-to-speech.watson.cloud.ibm.com/instances/xxxxx`)

**Save these credentials!**

```
WATSONX_TTS_API_KEY=your_api_key_here
WATSONX_TTS_URL=your_url_here
```

### 4. Create Speech to Text (STT) Service

#### A. Navigate to Catalog
1. Click **Catalog** in the top menu
2. Search for "Speech to Text"
3. Click on **Speech to Text**

#### B. Create Service Instance
1. Select your region
2. Choose a pricing plan:
   - **Lite** (Free): 500 minutes/month
   - **Standard**: Pay as you go
3. Name it (e.g., "ImpactGuard-STT")
4. Click **Create**

#### C. Get API Credentials
1. Click **Manage** in the left sidebar
2. Copy:
   - **API Key**
   - **URL** (looks like: `https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/xxxxx`)

**Save these credentials!**

```
WATSONX_STT_API_KEY=your_api_key_here
WATSONX_STT_URL=your_url_here
```

## Alternative: View All Services

### Method 1: Resource List
1. Go to [https://cloud.ibm.com/resources](https://cloud.ibm.com/resources)
2. You'll see all your services listed
3. Click on any service name
4. Click **Manage** → View credentials

### Method 2: Service Credentials Page
1. From your service page, click **Service credentials** in the left sidebar
2. If no credentials exist, click **New credential**
3. Give it a name and click **Add**
4. Click **View credentials** to see the JSON with API key and URL

## Example Credentials JSON

When you view credentials, you'll see something like:

```json
{
  "apikey": "aBcDeFgHiJkLmNoPqRsTuVwXyZ123456789",
  "iam_apikey_description": "Auto-generated for key...",
  "iam_apikey_name": "Auto-generated service credentials",
  "iam_role_crn": "crn:v1:bluemix:public:iam::::serviceRole:Manager",
  "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::...",
  "url": "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/xxxxx"
}
```

**You need:**
- `apikey` → Your API Key
- `url` → Your Service URL

## Configure ImpactGuard

### 1. Copy Environment Template

```bash
cp .env.example .env
```

### 2. Edit .env File

Open `.env` in your text editor and paste your credentials:

```bash
# WatsonX NLU (Natural Language Understanding)
WATSONX_NLU_API_KEY=aBcDeFgHiJkLmNoPqRsTuVwXyZ123456789
WATSONX_NLU_URL=https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/xxxxx
WATSONX_NLU_VERSION=2022-04-07

# WatsonX TTS (Text-to-Speech)
WATSONX_TTS_API_KEY=xYzAbC123456789dEfGhIjKlMnOpQrStUv
WATSONX_TTS_URL=https://api.us-south.text-to-speech.watson.cloud.ibm.com/instances/yyyyy
WATSONX_TTS_VOICE=en-US_AllisonV3Voice

# WatsonX STT (Speech-to-Text)
WATSONX_STT_API_KEY=123456789aBcDeFgHiJkLmNoPqRsTuVwXyZ
WATSONX_STT_URL=https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/zzzzz
WATSONX_STT_MODEL=en-US_BroadbandModel
```

### 3. Save and Test

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py

# Test in another terminal
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "services": {
    "nlu": true,
    "tts": true,
    "stt": true
  }
}
```

## Troubleshooting

### Can't Find API Key?

**Solution 1: Regenerate Credentials**
1. Go to your service page
2. Click **Service credentials**
3. Click **New credential**
4. Name it and click **Add**
5. View the new credentials

**Solution 2: Check Manage Tab**
1. Go to your service
2. Click **Manage** in left sidebar
3. Credentials should be visible at the top

### Wrong Region?

If your URL shows a different region (e.g., `eu-gb` instead of `us-south`):
- This is fine! Just use the URL provided
- Each service can be in a different region

### Service Not Listed?

1. Go to [IBM Cloud Catalog](https://cloud.ibm.com/catalog)
2. Search for the service
3. Create a new instance
4. Follow the steps above

### API Key Not Working?

1. **Check for spaces**: Make sure there are no spaces before/after the key
2. **Verify service is active**: Go to [Resource List](https://cloud.ibm.com/resources)
3. **Check region**: Ensure URL matches your service region
4. **Regenerate key**: Create new credentials if needed

## Security Best Practices

1. **Never commit .env file**
   - Already in `.gitignore`
   - Keep credentials private

2. **Use separate keys for dev/prod**
   - Create different service instances
   - Use different credentials

3. **Rotate keys regularly**
   - Delete old credentials
   - Create new ones every few months

4. **Monitor usage**
   - Check IBM Cloud dashboard
   - Set up billing alerts

## Free Tier Limits

### Natural Language Understanding
- **30,000 NLU items/month**
- Resets monthly
- Upgrade if you need more

### Text to Speech
- **10,000 characters/month**
- ~5-10 minutes of speech
- Upgrade for more

### Speech to Text
- **500 minutes/month**
- ~8 hours of audio
- Upgrade for more

## Quick Reference

| Service | Free Tier | Upgrade Cost |
|---------|-----------|--------------|
| NLU | 30K items/month | $0.003/item |
| TTS | 10K chars/month | $0.02/1K chars |
| STT | 500 min/month | $0.02/minute |

## Need Help?

1. **IBM Cloud Documentation**: [https://cloud.ibm.com/docs](https://cloud.ibm.com/docs)
2. **Watson Services**: [https://www.ibm.com/watson](https://www.ibm.com/watson)
3. **Support**: [https://cloud.ibm.com/unifiedsupport/supportcenter](https://cloud.ibm.com/unifiedsupport/supportcenter)

## Video Tutorial

IBM provides video tutorials:
1. Go to your service page
2. Look for "Getting Started" or "Documentation"
3. Watch the setup video

## Next Steps

Once you have your credentials configured:

1. ✅ Test the health endpoint
2. ✅ Try a simple query: `POST /conversation/query`
3. ✅ Test voice input/output
4. ✅ Read [WATSONX_INTEGRATION.md](WATSONX_INTEGRATION.md) for examples
5. ✅ Start building!

---

**Pro Tip**: Bookmark your [IBM Cloud Resource List](https://cloud.ibm.com/resources) for quick access to all your services!