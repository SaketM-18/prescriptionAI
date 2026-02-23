# Local Setup Guide

## Quick Fix for "Cannot Read Prescription" Error

### Problem
Your `key.json` has a placeholder value instead of a real Google API key.

### Solution

1. **Get your Google API Key**
   - Go to: https://aistudio.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key (it will look like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)

2. **Update key.json**
   - Open `key.json` in your editor
   - Replace `"your-actual-api-key-here"` with your actual key
   - Save the file

   Example:
   ```json
   {
     "api_key": "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
   }
   ```

3. **Test your setup**
   ```bash
   python test_setup.py
   ```

4. **Run the app**
   ```bash
   python app.py
   ```

## Common Issues

### "All models are busy"
This usually means:
- Invalid API key
- Rate limit exceeded (wait a few minutes)
- API key not enabled for Gemini API

**Fix:**
1. Verify your API key is correct
2. Go to https://aistudio.google.com/app/apikey
3. Make sure the key is enabled
4. Wait 2-3 minutes if you've been testing a lot

### "Cannot read prescription"
This means:
- Image quality is poor (blurry, dark)
- API key issue
- Network connection problem

**Fix:**
1. Take a clear, well-lit photo
2. Make sure text is readable
3. Check your internet connection

## Security Reminder

⚠️ **NEVER push key.json to GitHub!**

The file is already in `.gitignore`, but double-check:
```bash
git status
```

If you see `key.json` in the list, run:
```bash
git reset key.json
```

## Need Help?

Run the test script to diagnose issues:
```bash
python test_setup.py
```

It will tell you exactly what's wrong and how to fix it.
