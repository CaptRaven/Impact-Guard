# 🎨 ImpactGuard Demo UI Guide

## Quick Start

### 1. Start the Server
```bash
# Activate conda environment
conda activate impactguard

# Start the server
python main.py
```

The server will start at: **http://localhost:8000**

### 2. Access the Demo UI

Open your browser and navigate to:
```
http://localhost:8000
```

You'll see a beautiful, modern interface with three tabs:

## 📊 Features

### Tab 1: Analyze Files
**Purpose:** Perform comprehensive impact analysis on code changes

**How to Use:**
1. Enter your repository path (default: `/Users/mac/Documents/Impact Guard`)
2. Enter file paths to analyze (one per line), for example:
   ```
   main.py
   config.py
   models.py
   ```
3. Click "🔍 Analyze Impact"

**What You'll See:**
- **Risk Badge:** Visual indicator (LOW/MEDIUM/HIGH)
- **Risk Score:** Percentage-based risk assessment
- **Affected Areas:** Modules and services impacted
- **Critical Files:** Files requiring special attention
- **Warnings:** Potential issues and historical patterns
- **Suggested Reviewers:** Team members with expertise (with confidence scores)
- **Learning Path:** Files to understand before making changes

### Tab 2: Quick Summary
**Purpose:** Get a concise text summary of the impact

**How to Use:**
1. Enter repository path
2. Enter file paths to analyze
3. Click "📊 Get Summary"

**What You'll See:**
- Risk level badge
- Concise text summary of the analysis
- Key points about the changes

### Tab 3: System Health
**Purpose:** Check system status and available features

**Quick Actions:**
- **💚 Health Check:** Verify all services are running
- **ℹ️ API Info:** View API details and feature status
- **📚 API Docs:** Open interactive API documentation (Swagger UI)

## 🎯 Example Workflows

### Workflow 1: Analyze Your Current Changes
```
1. Go to "Analyze Files" tab
2. Keep default repo path: /Users/mac/Documents/Impact Guard
3. Enter files you've modified:
   main.py
   static/index.html
4. Click "Analyze Impact"
5. Review the risk assessment and warnings
6. Check suggested reviewers
7. Follow the learning path if risk is HIGH
```

### Workflow 2: Quick Health Check
```
1. Go to "System Health" tab
2. Click "💚 Health Check"
3. Verify all services are operational
4. Check WatsonX integration status
```

### Workflow 3: Explore API Documentation
```
1. Go to "System Health" tab
2. Click "📚 API Docs"
3. Interactive Swagger UI opens in new tab
4. Test endpoints directly from the browser
```

## 🎨 UI Features

### Visual Design
- **Modern Gradient Background:** Purple gradient for professional look
- **Card-Based Layout:** Clean, organized information display
- **Color-Coded Risk Levels:**
  - 🟢 LOW: Green badge
  - 🟡 MEDIUM: Yellow badge
  - 🔴 HIGH: Red badge
- **Smooth Animations:** Hover effects and transitions
- **Responsive Design:** Works on desktop and mobile

### Interactive Elements
- **Loading Spinner:** Shows during analysis
- **Error Messages:** Clear error display if something goes wrong
- **Confidence Bars:** Visual representation of reviewer confidence
- **Tabbed Interface:** Easy navigation between features

## 🔧 Troubleshooting

### Issue: "Cannot connect to server"
**Solution:**
```bash
# Make sure server is running
python main.py

# Check if port 8000 is available
lsof -i :8000
```

### Issue: "Repository not found"
**Solution:**
- Verify the repository path is correct
- Use absolute paths (e.g., `/Users/mac/Documents/Impact Guard`)
- Ensure the directory is a git repository

### Issue: "File not found"
**Solution:**
- Check file paths are relative to repository root
- Don't include leading slashes for file paths
- Example: Use `main.py` not `/main.py`

### Issue: WatsonX features show "Not Configured"
**Solution:**
- This is expected if you haven't set up IBM Cloud credentials yet
- Core features work without WatsonX
- See `IBM_CREDENTIALS_GUIDE.md` to enable AI features

## 📱 API Endpoints Used by UI

The demo UI interacts with these endpoints:

1. **POST /analyze/files** - Main analysis endpoint
2. **POST /summary** - Quick summary generation
3. **GET /health** - System health check
4. **GET /api** - API information
5. **GET /docs** - Interactive API documentation

## 🚀 Advanced Usage

### Testing with Different Repositories
```javascript
// In browser console, you can test with any repo:
fetch('http://localhost:8000/analyze/files', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        repository_path: '/path/to/your/repo',
        file_paths: ['src/main.py', 'src/utils.py']
    })
}).then(r => r.json()).then(console.log);
```

### Customizing the UI
The UI is a single HTML file at `static/index.html`:
- Modify colors in the `<style>` section
- Add new tabs by duplicating tab structure
- Customize API calls in the `<script>` section

## 🎓 Learning Resources

### Understanding the Results

**Risk Score Calculation:**
- Based on multiple factors (critical files, dependencies, history)
- Range: 0.0 (no risk) to 1.0 (maximum risk)
- Thresholds: <0.3 LOW, 0.3-0.7 MEDIUM, >0.7 HIGH

**Reviewer Confidence:**
- Based on commit history and expertise
- Higher confidence = more familiar with the code
- Multiple reviewers suggested for redundancy

**Learning Path Priority:**
- Files ordered by importance
- "Critical" files should be reviewed first
- Includes context about why each file matters

## 💡 Tips for Best Results

1. **Analyze Related Files Together:** Include all files in a feature
2. **Check History Tab:** Review past issues before making changes
3. **Follow Learning Path:** Understand dependencies before editing
4. **Review Warnings Carefully:** Historical patterns are valuable
5. **Consider Suggested Reviewers:** They know the code best

## 🎉 Demo Scenarios

### Scenario 1: Low-Risk Change
```
Files: README.md, docs/guide.md
Expected: LOW risk, minimal warnings, documentation reviewers
```

### Scenario 2: Medium-Risk Change
```
Files: services/impact_service.py, analyzers/change_analyzer.py
Expected: MEDIUM risk, some warnings, technical reviewers
```

### Scenario 3: High-Risk Change
```
Files: main.py, config.py, models.py
Expected: HIGH risk, multiple warnings, senior reviewers, detailed learning path
```

## 📞 Support

If you encounter issues:
1. Check the console for error messages (F12 in browser)
2. Verify server logs in terminal
3. Review `SETUP_INSTRUCTIONS.md` for configuration
4. Check `INSTALLATION_FIX.md` for common problems

## 🎯 Next Steps

After testing the demo:
1. ✅ Verify all features work correctly
2. 📝 Document any issues or improvements
3. 🔧 Configure WatsonX for AI features (optional)
4. 🚀 Integrate with your development workflow
5. 📊 Analyze real code changes in your projects

---

**Enjoy using ImpactGuard! 🛡️**