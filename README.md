# Prescription AI - Medical Prescription Reader

AI-powered prescription reading application that helps patients understand their medications in multiple languages.

## Features

- 📸 Upload prescription images
- 🤖 AI-powered text extraction using Google Gemini
- 🌍 Multi-language support (English, Hindi, Kannada, Tamil, Telugu, Malayalam)
- 🔊 Text-to-speech for medication instructions
- ⏰ Alarm reminders (opens native Clock app on mobile)
- 📱 Progressive Web App (PWA) - works offline
- 💾 Save prescription history
- 👥 Multiple user profiles

## Setup

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create API key file:**
```bash
# Create key.json in project root
echo '{"api_key": "your-google-api-key"}' > key.json
```

3. **Run the app:**
```bash
python app.py
```

4. **Visit:** http://localhost:5000

### Production (Render)

1. **Set environment variable:**
   - Go to Render Dashboard → Environment
   - Add: `GOOGLE_API_KEY` = your-api-key

2. **Deploy:**
   - Push to GitHub
   - Render auto-deploys

## API Key Configuration

The app uses `config.py` to load API keys:

- **Local:** Reads from `key.json` file
- **Production:** Reads from `GOOGLE_API_KEY` environment variable

Priority: Environment variable → key.json → error

## Security

⚠️ **IMPORTANT:**
- Never commit `key.json` to git (already in `.gitignore`)
- Never hardcode API keys in code
- Use environment variables in production
- See `SECURITY_FIX_URGENT.md` for security guidelines

## Project Structure

```
prescription_ai/
├── app.py                 # Main Flask application
├── pipeline.py            # AI processing pipeline
├── config.py              # API key configuration
├── templates/
│   ├── index.html        # Main UI
│   └── language.html     # Language selector
├── static/
│   ├── audio/            # Generated audio files
│   └── *.svg             # Logo files
├── key.json              # Local API key (not in git)
├── requirements.txt      # Python dependencies
└── Procfile              # Render deployment config
```

## Technologies

- **Backend:** Flask (Python)
- **AI:** Google Gemini 2.5 Flash
- **TTS:** Google Text-to-Speech (gTTS)
- **Frontend:** HTML, CSS, JavaScript
- **PWA:** Service Worker, Manifest

## Documentation

- `design.md` - System architecture and design
- `requirements.md` - Project requirements
- `SECURITY_FIX_URGENT.md` - Security guidelines
- `SECURITY_ACTION_CHECKLIST.md` - Security checklist

## License

Private project - All rights reserved
