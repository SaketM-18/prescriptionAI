# 🏠 Local Development - Quick Start

## ✅ Your Setup is Ready!

Your project is configured to work seamlessly in both environments:

### 🏠 Local Development
- Uses `key.json` file
- Already configured ✅
- Won't be pushed to Git (in `.gitignore`)

### ☁️ Production (Render)
- Uses `GOOGLE_API_KEY` environment variable
- Set in Render dashboard
- Automatically switches when deployed

## 🚀 Run Locally Now

```bash
# 1. Install dependencies (if not done)
pip install -r requirements.txt

# 2. Test your setup
python test_local.py

# 3. Run the app
python app.py
```

Then visit: **http://localhost:5000**

## 📋 What I Fixed

### Problem
- App was looking for `GOOGLE_API_KEY` environment variable
- You have the key in `key.json` for local development

### Solution
Created `config.py` that automatically:
1. ✅ Checks environment variable first (production)
2. ✅ Falls back to `key.json` (local)
3. ✅ Shows clear error if neither found

### Files Changed
- ✅ `pipeline.py` - Now uses `config.py`
- ✅ `config.py` - New helper for API key loading
- ✅ `.gitignore` - Already has `key.json` ✅

## 🧪 Test Your Setup

```bash
python test_local.py
```

Should show:
```
✅ PASS - API Key
✅ PASS - Imports
✅ PASS - Image Processing
✅ PASS - API Connection
✅ PASS - Full Pipeline

🎉 All tests passed!
```

## 📁 Your File Structure

```
prescription_ai/
├── key.json              ✅ Local API key (gitignored)
├── config.py             ✅ API key helper (new)
├── pipeline.py           ✅ Updated to use config.py
├── app.py                ✅ Flask app (unchanged)
├── test_local.py         ✅ Test script (new)
├── .gitignore           ✅ Excludes key.json
└── requirements.txt      ✅ Dependencies
```

## 🔑 How API Key Loading Works

```python
# Priority order:
1. Environment variable (GOOGLE_API_KEY)
   └─> Used in production (Render)

2. key.json file
   └─> Used in local development

3. Error if neither found
   └─> Clear message to user
```

## 🎯 Development Workflow

### Local Development
```bash
# 1. Make changes
# Edit files...

# 2. Test locally
python app.py
# Visit http://localhost:5000

# 3. Commit (key.json won't be included)
git add .
git commit -m "Your changes"
git push origin main
```

### Production Deployment
```bash
# Render automatically:
1. Detects your push
2. Deploys new code
3. Uses environment variable GOOGLE_API_KEY
4. Ignores key.json (not in repo)
```

## ✅ Verification Checklist

- [x] `key.json` exists with your API key
- [x] `key.json` is in `.gitignore`
- [x] `config.py` created
- [x] `pipeline.py` updated
- [x] `test_local.py` created
- [ ] Run `python test_local.py` ← Do this now!
- [ ] Run `python app.py` ← Then this!

## 🐛 Troubleshooting

### "API key not found"
```bash
# Check if key.json exists
cat key.json

# Should show:
# {"api_key": "AIzaSyCsy7ChWxKWUK4QvY6ElDKC7K-hfzltVi4"}
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:5000 | xargs kill -9
```

## 📚 Documentation

- `LOCAL_SETUP.md` - Detailed local setup guide
- `TROUBLESHOOTING.md` - Common issues and solutions
- `DEPLOY_NOW.md` - Deployment guide
- `test_local.py` - Test your setup

## 🎉 You're Ready!

Your local development environment is configured and ready to use!

**Next Steps:**
1. Run `python test_local.py` to verify
2. Run `python app.py` to start the server
3. Visit http://localhost:5000
4. Upload a prescription to test

**When deploying:**
- Just `git push` - Render handles the rest
- `key.json` won't be pushed (it's gitignored)
- Render uses environment variable automatically

Happy coding! 🚀
