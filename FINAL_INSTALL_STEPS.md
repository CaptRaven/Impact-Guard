# Final Installation Steps - WORKING SOLUTION

## The Issue
The `ibm-cloud-sdk-core==3.19.0` version has a build issue with Python 3.10.

## ✅ WORKING SOLUTION

Run these commands in order:

```bash
# 1. Activate environment
conda activate impactguard

# 2. Install setuptools with pkg_resources
pip install --upgrade pip
pip install setuptools==69.5.1

# 3. Install IBM Watson SDK with --no-build-isolation
pip install --no-build-isolation ibm-cloud-sdk-core
pip install ibm-watson

# 4. Install everything else
pip install fastapi uvicorn pydantic pydantic-settings python-multipart
pip install gitpython python-dotenv numpy scikit-learn
pip install sentence-transformers pyttsx3 aiofiles
```

## Alternative: Use Pre-built Wheels

```bash
conda activate impactguard

# Install from conda-forge (has pre-built packages)
pip install --upgrade pip setuptools wheel

# Install IBM packages without building
pip install --prefer-binary ibm-watson ibm-cloud-sdk-core

# Install rest
pip install fastapi uvicorn pydantic pydantic-settings python-multipart gitpython python-dotenv numpy scikit-learn sentence-transformers pyttsx3 aiofiles
```

## Fastest Solution: Skip IBM Watson for Now

If you want to test the core functionality first:

```bash
conda activate impactguard

# Install everything EXCEPT IBM Watson
pip install fastapi uvicorn pydantic pydantic-settings python-multipart
pip install gitpython python-dotenv numpy scikit-learn
pip install sentence-transformers pyttsx3 aiofiles

# Start the server (will work with fallback voice and rule-based NLU)
python main.py

# Test it
curl http://localhost:8000/health
```

The system will work with:
- ✅ All core analysis features
- ✅ Risk scoring
- ✅ Reviewer suggestions
- ✅ Learning paths
- ✅ Historical analysis
- ✅ Fallback TTS (pyttsx3)
- ✅ Rule-based NLU (no AI, but functional)

You can add IBM Watson later when you have the credentials.

## Install IBM Watson Later

When you're ready:

```bash
conda activate impactguard
pip install setuptools==69.5.1
pip install --no-build-isolation ibm-cloud-sdk-core
pip install ibm-watson
```

## Verify Installation

```bash
# Test core functionality
python -c "import fastapi; print('✅ FastAPI')"
python -c "import git; print('✅ GitPython')"
python -c "from services import ImpactService; print('✅ Core Services')"

# Test IBM Watson (if installed)
python -c "import ibm_watson; print('✅ IBM Watson')"
python -c "from services import ConversationalService; print('✅ Conversational AI')"
```

## Start Using ImpactGuard

```bash
# Configure (optional for now)
cp .env.example .env

# Start server
python main.py

# Test in another terminal
curl http://localhost:8000/
curl http://localhost:8000/health
```

## Test Core Features Without Watson

```bash
# Test analysis endpoint
curl -X POST http://localhost:8000/analyze/files \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "/path/to/your/repo",
    "file_paths": ["some_file.py"]
  }'
```

## Summary

**Option 1: Full Install (with IBM Watson)**
- Use `--no-build-isolation` flag
- May take longer
- Requires build tools

**Option 2: Core Install (without IBM Watson)**  
- Faster installation
- Works immediately
- Add Watson later

**Option 3: Use Updated requirements.txt**
- Now uses newer versions
- Should work better
- Run: `pip install -r requirements.txt`

## My Recommendation

Start with Option 2 (core install without Watson):
1. Get the system running quickly
2. Test all core features
3. Get your IBM credentials
4. Add Watson integration later

This way you can start using ImpactGuard immediately!

## Commands to Copy-Paste

### Quick Start (No Watson)
```bash
conda activate impactguard
pip install fastapi uvicorn pydantic pydantic-settings python-multipart gitpython python-dotenv numpy scikit-learn sentence-transformers pyttsx3 aiofiles
python main.py
```

### Add Watson Later
```bash
conda activate impactguard
pip install setuptools==69.5.1
pip install --no-build-isolation ibm-cloud-sdk-core
pip install ibm-watson
```

Choose what works best for you! 🚀