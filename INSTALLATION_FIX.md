# Installation Fix Guide

## Issue: ibm-cloud-sdk-core Installation Error

If you encountered this error:
```
ModuleNotFoundError: No module named 'pkg_resources'
ERROR: Failed to build 'ibm-cloud-sdk-core'
```

## Quick Fix (3 Steps)

### Step 1: Activate Environment
```bash
conda activate impactguard
```

### Step 2: Upgrade Build Tools
```bash
pip install --upgrade pip setuptools wheel
```

### Step 3: Install Dependencies in Order

**Option A: Use the install script**
```bash
bash install_requirements.sh
```

**Option B: Manual installation (recommended if script fails)**
```bash
# 1. Install core dependencies first
pip install fastapi uvicorn pydantic pydantic-settings python-multipart python-dotenv

# 2. Install IBM Watson SDK
pip install ibm-watson ibm-cloud-sdk-core

# 3. Install remaining dependencies
pip install gitpython numpy scikit-learn sentence-transformers pyttsx3 aiofiles
```

**Option C: Install from updated requirements.txt**
```bash
pip install -r requirements.txt
```
(The requirements.txt has been updated with proper ordering)

## Alternative Solutions

### Solution 1: Install with --no-build-isolation
```bash
pip install --upgrade setuptools
pip install --no-build-isolation ibm-cloud-sdk-core
pip install ibm-watson
pip install -r requirements.txt
```

### Solution 2: Use conda for some packages
```bash
conda install -c conda-forge setuptools pip wheel
pip install -r requirements.txt
```

### Solution 3: Install specific versions
```bash
pip install setuptools==69.0.0
pip install ibm-cloud-sdk-core==3.19.0
pip install ibm-watson==8.0.0
```

## Verify Installation

After installation, verify everything works:

```bash
# Test imports
python -c "import fastapi; print('✅ FastAPI OK')"
python -c "import ibm_watson; print('✅ IBM Watson OK')"
python -c "import ibm_cloud_sdk_core; print('✅ IBM SDK Core OK')"
python -c "from services import ConversationalService; print('✅ All services OK')"
```

## Still Having Issues?

### Check Python Version
```bash
python --version
# Should be Python 3.10.x
```

### Check pip Version
```bash
pip --version
# Should be pip 24.0 or higher
```

### Reinstall Environment
```bash
conda deactivate
conda env remove -n impactguard
conda create -n impactguard python=3.10 -y
conda activate impactguard
pip install --upgrade pip setuptools wheel
bash install_requirements.sh
```

### Install Without IBM Watson (Temporary)

If you want to test the core functionality without WatsonX:

```bash
# Install everything except IBM Watson
pip install fastapi uvicorn pydantic pydantic-settings
pip install gitpython python-dotenv numpy scikit-learn
pip install sentence-transformers pyttsx3 aiofiles python-multipart

# The system will work with fallback voice and rule-based NLU
python main.py
```

## Common Errors and Solutions

### Error: "No module named 'pkg_resources'"
**Solution:** Install setuptools first
```bash
pip install --upgrade setuptools
```

### Error: "Building wheel for ibm-cloud-sdk-core failed"
**Solution:** Install build dependencies
```bash
pip install --upgrade pip setuptools wheel build
```

### Error: "Microsoft Visual C++ required" (Windows)
**Solution:** Install Visual C++ Build Tools or use conda
```bash
conda install -c conda-forge ibm-cloud-sdk-core
```

### Error: "Command 'gcc' failed" (Linux/Mac)
**Solution:** Install development tools
```bash
# Mac
xcode-select --install

# Linux (Ubuntu/Debian)
sudo apt-get install build-essential python3-dev
```

## Success Checklist

- [ ] Conda environment created
- [ ] Environment activated
- [ ] pip/setuptools upgraded
- [ ] Core dependencies installed
- [ ] IBM Watson SDK installed
- [ ] All dependencies installed
- [ ] Imports verified
- [ ] Ready to configure credentials

## Next Steps After Successful Installation

1. **Configure Credentials**
   ```bash
   cp .env.example .env
   # Edit .env with your IBM WatsonX API keys
   ```

2. **Start Server**
   ```bash
   python main.py
   ```

3. **Test API**
   ```bash
   curl http://localhost:8000/health
   ```

## Need More Help?

- Check `SETUP_INSTRUCTIONS.md` for detailed setup guide
- See `IBM_CREDENTIALS_GUIDE.md` for API key setup
- Review `WATSONX_INTEGRATION.md` for usage examples

## Quick Command Reference

```bash
# Full installation sequence
conda activate impactguard
pip install --upgrade pip setuptools wheel
pip install fastapi uvicorn pydantic pydantic-settings python-multipart python-dotenv
pip install ibm-watson ibm-cloud-sdk-core
pip install gitpython numpy scikit-learn sentence-transformers pyttsx3 aiofiles

# Verify
python -c "from services import ConversationalService; print('✅ Success!')"

# Configure and run
cp .env.example .env
python main.py
```

Good luck! 🚀