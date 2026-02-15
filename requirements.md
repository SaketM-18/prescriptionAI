# Requirements Document

## Project Overview
**ClearScript** is an AI-powered prescription analysis web application designed to help rural villagers and non-technical users understand medical prescriptions. The application uses Google's Gemini AI to extract medicine information from prescription images and provides multilingual support with text-to-speech capabilities.

## Core Features

### 1. Prescription Image Analysis
- Upload prescription photos via file picker or camera
- AI-powered OCR and interpretation using Google Gemini Vision API
- Automatic extraction of medicine details:
  - Medicine name
  - Purpose/indication
  - Dosage (e.g., 1-0-1 format)
  - Timing (morning/afternoon/night with emoji indicators)
  - Duration
  - Warnings and precautions
  - Generic alternatives (cheaper options)

### 2. Multilingual Support
Supports 6 languages with full UI and content translation:
- English
- Hindi (हिंदी)
- Kannada (ಕನ್ನಡ)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Malayalam (മലയാളം)

Language selection wall on first visit with persistent session storage.

### 3. Drug Interaction Detection
- Automatic analysis of dangerous medicine combinations
- Severity classification (high/medium)
- Translated warnings in user's selected language
- Medical advice to consult doctor for dangerous combinations

### 4. Text-to-Speech (TTS)
- Audio playback of complete prescription guide
- Individual medicine instruction audio
- Language-specific voice synthesis using gTTS
- Purpose translation on-demand for audio generation

### 5. AI Chat Assistant
- Interactive Q&A about prescribed medicines
- Context-aware responses based on current prescription
- Voice input support (microphone)
- Multilingual responses
- Scope-limited to prescribed medicines only (no diagnosis)

### 6. Daily Schedule View
- Visual medicine schedule organized by time:
  - ☀️ Morning
  - 🌤️ Afternoon
  - 🌙 Night
- Alarm setting capability
- Tablet count display

### 7. Prescription History
- Save analyzed prescriptions
- View past prescriptions
- Delete saved records
- Date tracking
- Profile management (Myself + custom profiles)

### 8. Sharing Capabilities
- WhatsApp sharing with language selection
- Share prescription guide in any supported language
- Find nearby pharmacy integration

### 9. Progressive Web App (PWA)
- Installable on mobile devices
- Offline-capable service worker
- Standalone display mode
- Custom app icons and branding

## Technical Requirements

### Backend Stack
- **Framework**: Flask 3.1.0+
- **AI/ML**: Google Generative AI (Gemini) 1.62.0+
- **OCR**: Tesseract OCR via pytesseract 0.3.13+
- **TTS**: Google Text-to-Speech (gTTS) 2.5.0+
- **Image Processing**: Pillow 12.0.0+
- **Production Server**: Gunicorn 21.2.0+

### AI Models
Primary and fallback model strategy:
1. `gemini-2.0-flash` (primary)
2. `gemini-1.5-flash` (fallback 1)
3. `gemini-1.5-pro` (fallback 2)

### API Requirements
- Google Generative AI API key (environment variable: `GOOGLE_API_KEY`)
- Multimodal image analysis capability
- JSON response parsing with error handling

### File Storage
- `uploads/` - Prescription image storage
- `static/audio/` - Generated TTS audio files
- UUID-based filename generation for uniqueness

### Session Management
- Flask session with random secret key
- Language preference persistence
- Session invalidation on server restart

### Error Handling
- Image quality detection (blurry, dark)
- OCR failure recovery
- API quota exhaustion handling (429 errors)
- Model unavailability fallback (503/404 errors)
- Retry logic with exponential backoff
- User-friendly error messages

## Functional Requirements

### FR1: Image Upload
- Accept JPEG/JPG image formats
- Support file picker and camera capture
- Image preprocessing (resize to 1024x1024, 85% quality)
- Memory optimization with thumbnail generation

### FR2: Prescription Processing
- Extract structured medicine data from images
- Validate JSON response format
- Handle multiple medicines in single prescription
- Detect and report parsing errors

### FR3: Translation
- Translate all medicine details except brand names
- Maintain emoji indicators across languages
- Consistent field translations (timing/frequency, warnings/precautions)
- Dynamic purpose translation for TTS

### FR4: Audio Generation
- Generate comprehensive prescription audio guide
- Include all medicines and warnings
- Language-specific voice synthesis
- Unique audio file per generation

### FR5: Chat Interface
- Accept text and voice input
- Maintain medicine context
- Generate simple, village-friendly responses (2-3 sentences)
- Refuse off-topic questions
- Multilingual response generation

### FR6: Data Persistence
- Session-based language storage
- No database requirement (stateless design)
- File-based storage for uploads and audio

## Non-Functional Requirements

### NFR1: Performance
- Image processing within 10 seconds
- API response timeout handling
- Efficient memory management (cleanup after processing)
- Concurrent request handling via Gunicorn

### NFR2: Scalability
- Stateless application design
- Horizontal scaling capability
- Cloud deployment ready (Heroku Procfile included)
- Environment-based configuration

### NFR3: Reliability
- Multi-model fallback strategy
- Retry logic for transient failures
- Graceful degradation on API errors
- Error logging for debugging

### NFR4: Usability
- Mobile-first responsive design
- Simple, icon-based navigation
- Minimal text input requirements
- Voice interaction support
- Accessibility considerations (emoji indicators, audio)

### NFR5: Security
- No sensitive data storage
- Session-based authentication
- Environment variable for API keys
- File upload validation

### NFR6: Maintainability
- Modular code structure (app.py, pipeline.py)
- Configuration via environment variables
- Clear separation of concerns
- Comprehensive error messages

## Deployment Requirements

### Environment Variables
- `GOOGLE_API_KEY` - Required for Gemini API access
- `PORT` - Server port (default: 5000, Heroku-managed in production)

### Platform Support
- Heroku deployment (Procfile configured)
- Python 3.8+ runtime
- Tesseract OCR system dependency

### File System
- Write access to `uploads/` and `static/audio/`
- Automatic directory creation on startup

## User Workflows

### Workflow 1: First-Time User
1. Visit application
2. Select preferred language from language wall
3. Click "Start Analysis"
4. Upload prescription image
5. View extracted medicine details
6. Listen to audio guide
7. Ask questions via chat

### Workflow 2: Returning User
1. Visit application (language remembered)
2. View saved prescriptions or upload new
3. Switch language if needed
4. Share prescription via WhatsApp

### Workflow 3: Medicine Schedule
1. Upload prescription
2. Navigate to daily schedule view
3. Set alarms for medicine times
4. View organized by time of day

## Constraints & Limitations

### Technical Constraints
- Requires active internet connection
- Dependent on Google Gemini API availability
- API quota limitations (rate limiting)
- Image quality affects OCR accuracy

### Functional Constraints
- No medical diagnosis capability
- Limited to prescribed medicines only
- No drug database integration
- No doctor consultation features

### Language Constraints
- Limited to 6 Indian languages + English
- Translation quality depends on AI model
- No custom language addition without code changes

## Future Enhancements (Out of Scope)
- User authentication and accounts
- Cloud storage for prescriptions
- Doctor consultation integration
- Medicine reminder notifications
- Pharmacy inventory integration
- Offline OCR capability
- Additional language support
- Medicine interaction database
- Refill reminders
- Family member profiles with separate histories

## Success Criteria
- 90%+ prescription extraction accuracy
- <10 second processing time
- Support for 6+ languages
- Zero data loss on uploads
- 99% uptime for API calls (with fallbacks)
- Mobile-responsive on all devices
- PWA installation success rate >80%
