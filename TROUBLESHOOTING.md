# 🔧 Troubleshooting Guide

## Issue: "Could not read the prescription"

### Quick Fixes

#### 1. Check Render Logs
Go to your Render dashboard → Your service → Logs

Look for these messages:

**Good signs:**
```
📸 Original image: (2048, 1536), mode: RGB
📸 Preprocessed: (1536, 1152), 245678 bytes
🤖 Trying gemini-2.0-flash-exp...
✅ Success with gemini-2.0-flash-exp
```

**Problem signs:**
```
❌ GOOGLE_API_KEY not found
❌ Image processing error: ...
⚠️ gemini-2.0-flash-exp attempt 1: 404
❌ All models failed
```

#### 2. Verify API Key
1. Go to Render Dashboard
2. Click your service
3. Go to "Environment" tab
4. Check if `GOOGLE_API_KEY` exists
5. If not, add it:
   - Key: `GOOGLE_API_KEY`
   - Value: Your API key from Google AI Studio

#### 3. Check API Quota
1. Go to https://aistudio.google.com/
2. Check your API quota
3. If exceeded, wait or upgrade

#### 4. Test Locally
```bash
# Set API key
export GOOGLE_API_KEY="your-key-here"

# Test
python -c "from pipeline import run_pipeline; print(run_pipeline('sample.jpg', 'English'))"
```

### Common Errors & Solutions

#### Error: "API key not configured"
**Cause:** `GOOGLE_API_KEY` not set in Render environment  
**Solution:**
1. Render Dashboard → Environment
2. Add `GOOGLE_API_KEY` variable
3. Redeploy

#### Error: "404" or "Model not found"
**Cause:** Model name changed or not available  
**Solution:** The code tries 4 different models automatically. If all fail:
1. Check Google AI Studio for available models
2. Update model names in `pipeline.py`

#### Error: "429" or "Quota exceeded"
**Cause:** Too many API requests  
**Solution:**
1. Wait 1 minute
2. Or upgrade API quota at https://console.cloud.google.com/

#### Error: "Image processing failed"
**Cause:** Corrupted image or unsupported format  
**Solution:**
1. Ensure image is JPEG/JPG
2. Try a different image
3. Check image file size (< 10MB)

### Debugging Steps

#### Step 1: Check Deployment
```bash
# Check if latest code is deployed
git log -1
# Should show your latest commit
```

#### Step 2: Check Logs
In Render dashboard, look for:
- Deployment success message
- Any Python errors
- API call attempts
- Model responses

#### Step 3: Test API Key
```bash
# Test API key locally
python -c "
import os
from google import genai
api_key = os.environ.get('GOOGLE_API_KEY')
client = genai.Client(api_key=api_key)
print('API key works!')
"
```

#### Step 4: Test Image Processing
```bash
# Test image preprocessing
python -c "
from PIL import Image
from pipeline import preprocess_image
img = Image.open('sample.jpg')
processed = preprocess_image(img)
print(f'Processed: {processed.size}')
"
```

### Model Availability

The code tries these models in order:
1. `gemini-2.0-flash-exp` (Experimental, fastest)
2. `gemini-1.5-flash` (Stable, reliable)
3. `gemini-1.5-flash-8b` (Efficient)
4. `gemini-1.5-pro` (Most capable)

If all fail, check https://ai.google.dev/models for current model names.

### Image Quality Issues

#### Blurry Images
- Hold phone steady
- Use good lighting
- Avoid shaking

#### Dark Images
- Use flash or better lighting
- Avoid shadows
- Take photo near window

#### Glare/Reflections
- Avoid direct light on prescription
- Tilt prescription to avoid glare
- Use diffused lighting

### Still Not Working?

#### Check Requirements
```bash
# Verify all packages installed
pip list | grep -E "google-genai|Pillow|Flask"
```

Should show:
- `google-genai` >= 1.0.0
- `Pillow` >= 12.0.0
- `Flask` >= 3.1.0

#### Reinstall Dependencies
```bash
pip install --upgrade google-genai Pillow Flask
```

#### Check Python Version
```bash
python --version
# Should be 3.8 or higher
```

### Get Help

1. **Check Logs First** - Most issues show up in logs
2. **Test Locally** - Reproduce the issue on your machine
3. **Check API Status** - https://status.cloud.google.com/
4. **Verify Environment** - API key, Python version, packages

### Quick Test Script

Save as `test_prescription.py`:

```python
import os
from pipeline import run_pipeline

# Test
result = run_pipeline('sample.jpg', 'English')
print(result)
```

Run:
```bash
python test_prescription.py
```

### Emergency Rollback

If new code doesn't work, rollback:

```bash
# Revert to previous version
git revert HEAD
git push origin main
```

Render will auto-deploy the previous working version.

### Contact Support

If nothing works:
1. Copy error logs from Render
2. Note what you tried
3. Check if API key is valid
4. Verify image format (JPEG/JPG)
5. Test with different prescription images

### Success Indicators

When working correctly, you should see:
- ✅ Image preprocessed successfully
- ✅ Model responds with JSON
- ✅ Medicines extracted
- ✅ All fields populated
- ✅ No error messages

### Performance Tips

- Use clear, well-lit images
- JPEG format preferred
- File size < 5MB
- Avoid very high resolution (> 4000px)
- Hold prescription flat
- Capture entire prescription in frame
