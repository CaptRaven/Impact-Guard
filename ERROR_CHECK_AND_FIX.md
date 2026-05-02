# Error Check and Fix Guide

## Running Error Check

To identify errors in the code, run these commands:

### 1. Check for Syntax Errors

```bash
conda activate impactguard

# Check main.py
python -m py_compile main.py

# Check all Python files
find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" | xargs python -m py_compile
```

### 2. Check for Import Errors

```bash
# Test imports without IBM Watson
python -c "
try:
    from models import ImpactReport, ChangeInput
    print('✅ models.py - OK')
except Exception as e:
    print(f'❌ models.py - ERROR: {e}')

try:
    from config import settings
    print('✅ config.py - OK')
except Exception as e:
    print(f'❌ config.py - ERROR: {e}')

try:
    from analyzers import ChangeAnalyzer, RiskScorer
    print('✅ analyzers - OK')
except Exception as e:
    print(f'❌ analyzers - ERROR: {e}')

try:
    from services import ImpactService
    print('✅ services (core) - OK')
except Exception as e:
    print(f'❌ services (core) - ERROR: {e}')
"
```

### 3. Check WatsonX Services (Optional)

```bash
# Only if IBM Watson is installed
python -c "
try:
    from services import ConversationalService
    print('✅ WatsonX services - OK')
except ImportError as e:
    print('⚠️  WatsonX services - Not installed (this is OK if you skipped Watson)')
except Exception as e:
    print(f'❌ WatsonX services - ERROR: {e}')
"
```

## Common Errors and Fixes

### Error 1: ModuleNotFoundError for pydantic_settings

**Error:**
```
ModuleNotFoundError: No module named 'pydantic_settings'
```

**Fix:**
```bash
pip install pydantic-settings
```

### Error 2: ModuleNotFoundError for ibm_watson

**Error:**
```
ModuleNotFoundError: No module named 'ibm_watson'
```

**Fix (if you want Watson):**
```bash
pip install setuptools==69.5.1
pip install --no-build-isolation ibm-cloud-sdk-core
pip install ibm-watson
```

**Or skip Watson for now:**
- The system will work without it
- WatsonX services will show warnings but won't crash

### Error 3: Import errors in services/__init__.py

**Error:**
```
ImportError: cannot import name 'ConversationalService'
```

**Fix:**
Comment out WatsonX imports if not installed:

```python
# Edit services/__init__.py
from .voice_service import VoiceService
from .impact_service import ImpactService

# Comment these out if IBM Watson not installed:
# from .watsonx_nlu_service import WatsonXNLUService
# from .watsonx_tts_service import WatsonXTTSService
# from .watsonx_stt_service import WatsonXSTTService
# from .conversational_service import ConversationalService

__all__ = [
    "VoiceService",
    "ImpactService",
    # "WatsonXNLUService",  # Comment out
    # "WatsonXTTSService",  # Comment out
    # "WatsonXSTTService",  # Comment out
    # "ConversationalService"  # Comment out
]
```

### Error 4: ConversationalService not found in main.py

**Error:**
```
ImportError: cannot import name 'ConversationalService' from 'services'
```

**Fix:**
Comment out conversational features in main.py:

```python
# Line 14 in main.py - comment out if Watson not installed
from services import ImpactService  # , ConversationalService

# Line 34 - comment out
# conversational_service = ConversationalService()

# Comment out all /conversation/* endpoints (lines 72-245)
```

## Quick Fix Script

Create a file `fix_imports.py`:

```python
#!/usr/bin/env python3
"""
Quick fix script to handle missing IBM Watson dependencies
"""
import sys

def check_and_fix():
    print("Checking dependencies...")
    
    # Check core dependencies
    try:
        import fastapi
        print("✅ FastAPI installed")
    except ImportError:
        print("❌ FastAPI missing - run: pip install fastapi uvicorn")
        return False
    
    try:
        import git
        print("✅ GitPython installed")
    except ImportError:
        print("❌ GitPython missing - run: pip install gitpython")
        return False
    
    try:
        from models import ImpactReport
        print("✅ Models OK")
    except Exception as e:
        print(f"❌ Models error: {e}")
        return False
    
    # Check IBM Watson (optional)
    try:
        import ibm_watson
        print("✅ IBM Watson installed")
        watson_available = True
    except ImportError:
        print("⚠️  IBM Watson not installed (optional)")
        watson_available = False
    
    if not watson_available:
        print("\n" + "="*50)
        print("IBM Watson not installed")
        print("="*50)
        print("\nOptions:")
        print("1. Install Watson:")
        print("   pip install setuptools==69.5.1")
        print("   pip install --no-build-isolation ibm-cloud-sdk-core")
        print("   pip install ibm-watson")
        print("\n2. Or run without Watson (core features work fine)")
        print("\nTo disable Watson features:")
        print("   python fix_imports.py --disable-watson")
    
    return True

if __name__ == "__main__":
    if "--disable-watson" in sys.argv:
        print("Disabling Watson features...")
        # This would modify the imports
        print("Manual step: Comment out Watson imports in services/__init__.py")
        print("Manual step: Comment out conversational endpoints in main.py")
    else:
        check_and_fix()
```

Run it:
```bash
python fix_imports.py
```

## Testing After Fixes

### Test 1: Import Test
```bash
python -c "from services import ImpactService; print('✅ Core services work!')"
```

### Test 2: Start Server
```bash
python main.py
```

If it starts without errors, you're good!

### Test 3: API Test
```bash
# In another terminal
curl http://localhost:8000/
curl http://localhost:8000/health
```

## What to Do Based on Errors

### If you see: "No module named 'ibm_watson'"

**Option A:** Install IBM Watson (see FINAL_INSTALL_STEPS.md)

**Option B:** Run without Watson:
1. Comment out Watson imports in `services/__init__.py`
2. Comment out conversational endpoints in `main.py`
3. System works with core features

### If you see: "No module named 'pydantic_settings'"

```bash
pip install pydantic-settings
```

### If you see: "No module named 'git'"

```bash
pip install gitpython
```

### If you see: "No module named 'fastapi'"

```bash
pip install fastapi uvicorn
```

## Recommended Approach

1. **Install core dependencies first:**
   ```bash
   pip install fastapi uvicorn pydantic pydantic-settings python-multipart
   pip install gitpython python-dotenv numpy scikit-learn
   pip install sentence-transformers pyttsx3 aiofiles
   ```

2. **Test core functionality:**
   ```bash
   python -c "from services import ImpactService; print('OK')"
   ```

3. **Start server:**
   ```bash
   python main.py
   ```

4. **If it works, you're done!**

5. **Add Watson later** (optional):
   ```bash
   pip install setuptools==69.5.1
   pip install --no-build-isolation ibm-cloud-sdk-core
   pip install ibm-watson
   ```

## Summary

**Most likely issues:**
1. ✅ IBM Watson not installed → **Solution:** Run without it or install it
2. ✅ pydantic-settings missing → **Solution:** `pip install pydantic-settings`
3. ✅ Import errors → **Solution:** Comment out Watson imports

**The system WILL WORK without IBM Watson!**
- All core analysis features work
- Risk scoring works
- Reviewer suggestions work
- Historical analysis works
- Only conversational AI features need Watson

## Need Help?

Run this diagnostic:
```bash
python -c "
import sys
print(f'Python: {sys.version}')

try:
    import fastapi
    print('✅ FastAPI')
except: print('❌ FastAPI')

try:
    import git
    print('✅ GitPython')
except: print('❌ GitPython')

try:
    import pydantic
    print('✅ Pydantic')
except: print('❌ Pydantic')

try:
    import ibm_watson
    print('✅ IBM Watson')
except: print('⚠️  IBM Watson (optional)')

try:
    from services import ImpactService
    print('✅ Core Services')
except Exception as e:
    print(f'❌ Core Services: {e}')
"
```

Send me the output and I'll help you fix it!