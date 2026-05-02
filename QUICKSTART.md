# ImpactGuard Quick Start Guide

Get up and running with ImpactGuard in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Git repository with commit history
- pip package manager

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python test_impact_guard.py
```

This will run a test suite using the ImpactGuard project itself as a sample repository.

## Quick Usage Examples

### Example 1: Analyze Current Changes (CLI)

```bash
# Start the API server
python main.py
```

Then in another terminal:

```bash
# Analyze uncommitted changes in a repository
curl -X POST "http://localhost:8000/analyze/diff" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "/path/to/your/repo",
    "branch": "main"
  }'
```

### Example 2: Analyze Specific Files (Python)

```python
from services import ImpactService

# Initialize service with your repository
service = ImpactService("/path/to/your/repo")

# Analyze specific files
report = service.analyze_specific_files([
    "src/authentication/login.py",
    "src/payments/processor.py"
])

# Print results
print(f"Risk Level: {report.risk_level.value}")
print(f"Risk Score: {report.risk_score:.2f}")

# Show warnings
for warning in report.warnings:
    print(f"⚠️  {warning.message}")

# Show suggested reviewers
for reviewer in report.suggested_reviewers:
    print(f"👤 {reviewer.name} (confidence: {reviewer.confidence:.0%})")
```

### Example 3: Get Voice Summary

```python
from services import ImpactService

service = ImpactService("/path/to/your/repo")
report = service.analyze_specific_files(["src/auth.py"])

# Get voice summary
voice_summary = service.voice_service.generate_voice_summary(report)
print(voice_summary)

# Optionally speak it (requires TTS support)
service.voice_service.speak(voice_summary)
```

### Example 4: API Request with curl

```bash
# Analyze specific files
curl -X POST "http://localhost:8000/analyze/files" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "/path/to/your/repo",
    "file_paths": ["src/auth.py", "src/payment.py"]
  }'
```

### Example 5: Get Quick Summary

```bash
curl -X POST "http://localhost:8000/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "/path/to/your/repo",
    "file_paths": ["src/auth.py"]
  }'
```

## Understanding the Output

### Risk Levels

- **LOW** (0.0 - 0.3): Standard review process
- **MEDIUM** (0.3 - 0.6): Careful review recommended
- **HIGH** (0.6 - 1.0): Thorough review and testing required

### Key Metrics

- **Risk Score**: Overall risk assessment (0.0 to 1.0)
- **Affected Areas**: Modules/services impacted by changes
- **Critical Files**: Files requiring special attention
- **Warnings**: Specific concerns based on history and analysis
- **Suggested Reviewers**: Team members with relevant expertise
- **Learning Path**: Files to understand before making changes

## Common Use Cases

### Pre-Commit Analysis

```bash
# Before committing, analyze your changes
python -c "
from services import ImpactService
service = ImpactService('.')
report = service.analyze_impact(
    {'repository_path': '.', 'branch': 'main'}
)
print(service.get_quick_summary(report))
"
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/impact-analysis.yml
- name: Analyze Impact
  run: |
    pip install -r requirements.txt
    python -c "
    from services import ImpactService
    service = ImpactService('.')
    report = service.analyze_specific_files(['changed_file.py'])
    if report.risk_level.value == 'HIGH':
        print('⚠️  High risk changes detected!')
        exit(1)
    "
```

### Pre-Review Checklist

```python
from services import ImpactService

service = ImpactService("/path/to/repo")
report = service.analyze_specific_files(["your_file.py"])

print("Pre-Review Checklist:")
print(f"✓ Risk Level: {report.risk_level.value}")
print(f"✓ Reviewers: {', '.join([r.name for r in report.suggested_reviewers[:3]])}")
print(f"✓ Files to Study: {len(report.learning_path)}")

if report.warnings:
    print("\n⚠️  Warnings:")
    for w in report.warnings:
        print(f"  - {w.message}")
```

## Configuration

Create a `.env` file to customize settings:

```bash
cp .env.example .env
```

Edit `.env` to adjust:
- Risk thresholds
- Analysis depth
- Reviewer limits
- Voice settings

## Troubleshooting

### "Not a git repository" error
- Ensure you're analyzing a valid git repository
- Check that the repository path is correct

### No reviewers suggested
- Repository needs commit history
- Ensure files have been committed by multiple authors

### Voice output not working
- Install system TTS support (espeak on Linux, built-in on macOS/Windows)
- Check `VOICE_ENABLED` setting in config

### Import errors
- Run `pip install -r requirements.txt`
- Ensure Python 3.8+ is installed

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore the API at `http://localhost:8000/docs`
3. Customize settings in `config.py`
4. Integrate with your development workflow

## Support

For issues or questions:
- Check the README.md
- Review the code documentation
- Test with `test_impact_guard.py`

Happy coding! 🚀