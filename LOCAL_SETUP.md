# 🏠 Local Development Setup

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. API Key Setup

The app automatically detects whether you're running locally or in production:

**Local Development (your machine):**
- Uses `key.json` file
- Already configured ✅
- File is in `.gitignore` (won't be pushed to Git)

**Production (Render):**
- Uses `GOOGLE_API_KEY` environment variable
- Set in Render dashboard
- key.json is ignored

### 3. Run Locally
```bash
python app.py
```

Then visit: http://localhost:5000

## How It Works

### API Key Priority
1. **First**: Check environment variable `GOOGLE_API_KEY`
2. **Second**: Check `key.json` file
3. **If neither**: Show error

### Your Current Setup
```
key.json (local) ✅
├── api_key: "AIza...Vi4"
└── In .gitignore ✅

Render (production) ✅
└── Environment variable: GOOGLE_API_KEY
```

## Testing

### Test API Key Loading
```bash
python -c "from config import get_api_key; print('API Key:', get_api_key()[:10] + '...')"
```

Should show:
```
🔑 Using API key from key.json (local mode)
API Key: AIzaSyCsy7...
```

### Test Prescription Processing
```bash
python -c "
from pipeline import run_pipeline
import json

result = run_pipeline('sample.jpg', 'English')
data = json.loads(result)

if 'error' in data:
    print('❌ ERROR:', data['error'])
else:
    print('✅ SUCCESS:', len(data.get('english', [])), 'medicines found')
"
```

### Run Full App
```bash
# Start Flask server
python app.py

# In another terminal, test upload
curl -X POST http://localhost:5000/ \
  -F "language=English" \
  -F "image=@sample.jpg"
```

## File Structure

```
prescription_ai/
├── key.json              # Local API key (gitignored)
├── config.py             # API key helper
├── pipeline.py           # Prescription processing
├── app.py                # Flask application
├── requirements.txt      # Dependencies
├── .gitignore           # Excludes key.json
└── uploads/             # Uploaded images (gitignored)
```

## Common Issues

### "API key not found"
**Check:**
1. Does `key.json` exist?
2. Is it in the root directory?
3. Does it have the correct format?

**Fix:**
```bash
# Verify file exists
ls -la key.json

# Check content
cat key.json
# Should show: {"api_key": "AIza..."}
```

### "Module not found"
**Fix:**
```bash
pip install -r requirements.txt
```

### "Port already in use"
**Fix:**
```bash
# Kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:5000 | xargs kill -9
```

## Development Workflow

### 1. Make Changes
Edit files locally with your API key in `key.json`

### 2. Test Locally
```bash
python app.py
# Test at http://localhost:5000
```

### 3. Commit & Push
```bash
git add .
git commit -m "Your changes"
git push origin main
```

**Note:** `key.json` won't be pushed (it's in .gitignore)

### 4. Deploy to Render
Render automatically:
1. Detects the push
2. Deploys new code
3. Uses environment variable `GOOGLE_API_KEY`
4. Ignores `key.json` (not in repo)

## Environment Variables

### Local (.env file - optional)
You can also use a `.env` file:

```bash
# Create .env
echo "GOOGLE_API_KEY=AIzaSyCsy7ChWxKWUK4QvY6ElDKC7K-hfzltVi4" > .env

# Add to .gitignore
echo ".env" >> .gitignore

# Load in Python
pip install python-dotenv

# In app.py, add at top:
from dotenv import load_dotenv
load_dotenv()
```

But `key.json` is simpler and already working!

## Debugging

### Enable Debug Mode
```python
# In app.py, change:
if __name__ == "__main__":
    app.run(debug=True)  # Add debug=True
```

### Check Logs
```bash
# Run with verbose output
python app.py 2>&1 | tee app.log
```

### Test Individual Components
```bash
# Test image preprocessing
python -c "
from PIL import Image
from pipeline import preprocess_image
img = Image.open('sample.jpg')
processed = preprocess_image(img)
print(f'✅ Processed: {processed.size}')
"

# Test API connection
python -c "
from google import genai
from config import get_api_key
client = genai.Client(api_key=get_api_key())
print('✅ API connection works!')
"
```

## Production Deployment

### Before Deploying
- [ ] Test locally with `key.json`
- [ ] Verify `key.json` is in `.gitignore`
- [ ] Commit and push changes
- [ ] Verify `GOOGLE_API_KEY` is set in Render

### After Deploying
- [ ] Check Render logs
- [ ] Test prescription upload
- [ ] Verify API key is loaded from environment

## Security Notes

✅ **Good:**
- `key.json` in `.gitignore`
- API key not in code
- Environment variables in production

❌ **Never:**
- Commit `key.json` to Git
- Hardcode API key in code
- Share API key publicly

## Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Test API key
python -c "from config import get_api_key; print(get_api_key())"

# Test prescription
python -c "from pipeline import run_pipeline; print(run_pipeline('sample.jpg', 'English'))"

# Deploy
git add .
git commit -m "Update"
git push origin main
```

## Need Help?

1. Check logs for errors
2. Verify `key.json` format
3. Test API key loading
4. Check `TROUBLESHOOTING.md`

## Success!

When working correctly:
```
🔑 Using API key from key.json (local mode)
📸 Original image: (2048, 1536), mode: RGB
📸 Preprocessed: (1536, 1152), 245678 bytes
🤖 Trying gemini-2.0-flash-exp...
✅ Success with gemini-2.0-flash-exp
```

You're all set for local development! 🚀
