# ImpactGuard Setup Instructions (Conda)

Complete setup guide for ImpactGuard using Conda environment.

## Quick Setup (Automated)

Run the setup script:

```bash
./setup_conda.sh
```

This will:
1. Create conda environment named `impactguard`
2. Install Python 3.10
3. Install all dependencies from requirements.txt

## Manual Setup (Step-by-Step)

If you prefer to set up manually or the script doesn't work:

### Step 1: Create Conda Environment

```bash
conda create -n impactguard python=3.10 -y
```

### Step 2: Activate Environment

```bash
conda activate impactguard
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (API framework)
- Pydantic (data validation)
- GitPython (git operations)
- IBM Watson SDK (WatsonX services)
- NumPy, scikit-learn (analysis)
- sentence-transformers (embeddings)
- pyttsx3 (fallback TTS)
- And more...

### Step 4: Configure IBM WatsonX Credentials

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your IBM WatsonX credentials
nano .env  # or use your preferred editor
```

See [IBM_CREDENTIALS_GUIDE.md](IBM_CREDENTIALS_GUIDE.md) for how to get your API keys.

### Step 5: Verify Installation

```bash
# Check Python version
python --version
# Should show: Python 3.10.x

# Check installed packages
pip list | grep -E "fastapi|ibm-watson|gitpython"

# Test import
python -c "from services import ConversationalService; print('✅ Import successful!')"
```

### Step 6: Start the Server

```bash
python main.py
```

You should see:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 7: Test the API

Open a new terminal and test:

```bash
# Activate environment
conda activate impactguard

# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "services": {
#     "nlu": true,
#     "tts": true,
#     "stt": true
#   }
# }
```

## Troubleshooting

### Issue: Conda command not found

**Solution:**
```bash
# Initialize conda for your shell
conda init bash  # or zsh, fish, etc.

# Restart your terminal
```

### Issue: Environment activation fails

**Solution:**
```bash
# Use full path to conda
/opt/anaconda3/bin/conda activate impactguard

# Or source conda
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate impactguard
```

### Issue: pip install fails

**Solution:**
```bash
# Update pip first
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# If specific package fails, install individually
pip install fastapi uvicorn pydantic
pip install ibm-watson ibm-cloud-sdk-core
# ... etc
```

### Issue: Import errors

**Solution:**
```bash
# Verify you're in the correct environment
conda env list
# * should be next to impactguard

# Reinstall problematic package
pip uninstall <package-name>
pip install <package-name>
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use a different port
python main.py --port 8001

# Or kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

## Environment Management

### List all conda environments
```bash
conda env list
```

### Activate environment
```bash
conda activate impactguard
```

### Deactivate environment
```bash
conda deactivate
```

### Update environment
```bash
conda activate impactguard
pip install --upgrade -r requirements.txt
```

### Remove environment
```bash
conda deactivate
conda env remove -n impactguard
```

### Export environment
```bash
conda activate impactguard
conda env export > environment.yml
```

### Create from exported environment
```bash
conda env create -f environment.yml
```

## Development Setup

### Install development dependencies

```bash
conda activate impactguard

# Install testing tools
pip install pytest pytest-cov pytest-asyncio

# Install code quality tools
pip install black flake8 mypy

# Install documentation tools
pip install mkdocs mkdocs-material
```

### Run tests

```bash
python test_impact_guard.py
```

### Format code

```bash
black .
```

### Type checking

```bash
mypy .
```

## IDE Setup

### VS Code

1. Install Python extension
2. Select interpreter:
   - Cmd+Shift+P → "Python: Select Interpreter"
   - Choose: `Python 3.10.x ('impactguard')`

3. Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "/opt/anaconda3/envs/impactguard/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true
}
```

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Conda Environment"
4. Choose existing environment: `impactguard`

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn

gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM continuumio/miniconda3

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t impactguard .
docker run -p 8000:8000 --env-file .env impactguard
```

## Performance Tips

1. **Use conda-forge channel** for faster installs:
   ```bash
   conda config --add channels conda-forge
   ```

2. **Use mamba** for faster dependency resolution:
   ```bash
   conda install mamba -c conda-forge
   mamba install <package>
   ```

3. **Cache pip packages**:
   ```bash
   pip install --cache-dir ~/.cache/pip -r requirements.txt
   ```

## Next Steps

1. ✅ Environment created and activated
2. ✅ Dependencies installed
3. ⏭️ Configure IBM WatsonX credentials ([Guide](IBM_CREDENTIALS_GUIDE.md))
4. ⏭️ Start the server
5. ⏭️ Test with sample queries
6. ⏭️ Read [WATSONX_INTEGRATION.md](WATSONX_INTEGRATION.md) for usage examples

## Support

- **Conda Documentation**: https://docs.conda.io/
- **ImpactGuard Issues**: Check the README.md
- **IBM WatsonX**: See IBM_CREDENTIALS_GUIDE.md

## Quick Reference

```bash
# Create environment
conda create -n impactguard python=3.10 -y

# Activate
conda activate impactguard

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your API keys

# Start server
python main.py

# Test
curl http://localhost:8000/health
```

Happy coding! 🚀