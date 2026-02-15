# Design Document - ClearScript

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer (Browser)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   HTML/CSS   │  │  JavaScript  │  │  PWA/Service │      │
│  │   Templates  │  │   Frontend   │  │    Worker    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/HTTPS
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer (Flask)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   app.py     │  │  pipeline.py │  │ Translation  │      │
│  │  (Routes)    │  │  (AI Logic)  │  │   System     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕ API Calls
┌─────────────────────────────────────────────────────────────┐
│                    External Services Layer                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Google     │  │    gTTS      │  │  Tesseract   │      │
│  │   Gemini AI  │  │   (Audio)    │  │    (OCR)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                      Storage Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ localStorage │  │   uploads/   │  │static/audio/ │      │
│  │  (Browser)   │  │  (Images)    │  │   (MP3)      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Component Breakdown

#### Frontend Components
- **Language Selection Wall**: First-time user language preference
- **Tab Navigation**: Scan vs History views
- **Upload Interface**: File picker and camera capture
- **Results Display**: Medicine cards with detailed information
- **Schedule View**: Time-based medicine organization
- **Chat Interface**: AI-powered Q&A system
- **History Manager**: Saved prescriptions with filtering
- **Profile Manager**: Multi-user support

#### Backend Components
- **Flask Application** (`app.py`): Request routing, session management
- **AI Pipeline** (`pipeline.py`): Image processing, Gemini API integration
- **Translation Engine**: Multilingual content generation
- **TTS Generator**: Audio synthesis for instructions

## 2. Data Flow

### 2.1 Prescription Processing Flow

```
User Upload → Image Validation → AI Processing → JSON Parsing → 
Translation → TTS Generation → Display Results → Save to History
```

**Detailed Steps:**

1. **Image Upload**
   - User selects file or captures photo
   - Client-side quality check (brightness, blur detection)
   - Image uploaded to Flask server
   - Saved to `uploads/` with UUID filename

2. **AI Processing**
   - Image resized to 1024x1024 (memory optimization)
   - Sent to Google Gemini Vision API
   - Retry logic with model fallback:
     - Primary: `gemini-2.0-flash`
     - Fallback 1: `gemini-1.5-flash`
     - Fallback 2: `gemini-1.5-pro`
   - Exponential backoff for rate limiting (429 errors)

3. **Response Processing**
   - JSON response cleaned (remove markdown artifacts)
   - Parsed into structured medicine data
   - Validation of required fields

4. **Translation**
   - Medicine details translated to selected language
   - Brand names preserved in English
   - Emoji indicators maintained across languages

5. **Audio Generation**
   - Comprehensive prescription guide text compiled
   - gTTS synthesis with language-specific voice
   - Audio saved to `static/audio/` with UUID filename

6. **Display & Storage**
   - Results rendered in medicine cards
   - Schedule view generated from dosage patterns
   - Entry saved to localStorage with profile association

### 2.2 Chat Interaction Flow

```
User Question → Context Building → Gemini API → Response → 
TTS (optional) → Display Answer
```

**Context Building:**
- Current prescription medicines
- Medicine properties (dosage, purpose, timing)
- User's selected language
- Scope limitation (only prescribed medicines)

## 3. Database Design

### 3.1 Client-Side Storage (localStorage)

**History Entry Schema:**
```javascript
{
  "date": "2024-02-15 14:30",
  "language": "Hindi",
  "profile": "Myself",
  "medicines": [
    {
      "name": "Medicine Name",
      "medicine_name": "Medicine Name",
      "purpose": "Translated purpose",
      "dosage": "1-0-1",
      "visual_timing": "☀️ -- 🌙",
      "timing": "After food",
      "frequency": "After food",
      "duration": "5 days",
      "warnings": "Take with water",
      "precautions": "Take with water",
      "generic_alternative": "Generic name + description"
    }
  ]
}
```

**Profile Storage:**
```javascript
{
  "clearscript_profiles": ["Myself", "Father", "Mother", "Custom Name"],
  "selected_profile": "Myself"
}
```

**Session Storage:**
```javascript
{
  "user_lang": "Hindi"
}
```

### 3.2 Server-Side Storage

**File System Structure:**
```
uploads/
  ├── {uuid}.jpg          # Uploaded prescription images
  
static/audio/
  ├── {uuid}.mp3          # Generated TTS audio files
  ├── audio_{hash}.mp3    # Chat TTS responses
```

**No Database Required:**
- Stateless application design
- Session-based authentication
- Client-side history persistence
- Temporary file storage only

## 4. API Design

### 4.1 Flask Routes

#### `GET /`
**Purpose**: Main application page

**Response**: Rendered HTML template with:
- Language-specific translations
- Session language preference
- Results (if POST processed)

#### `POST /`
**Purpose**: Process prescription upload

**Request:**
```
Content-Type: multipart/form-data

Fields:
- language: string (English|Hindi|Kannada|Tamil|Telugu|Malayalam)
- image: file (JPEG/JPG)
- image_camera: file (alternative camera input)
```

**Response**: HTML with:
- `english`: Array of medicine objects (English)
- `translated`: Array of medicine objects (target language)
- `dangerous_combinations`: Array of interaction warnings
- `audio_path`: String path to TTS audio file
- `error_type`: String (if processing failed)

#### `GET /set_language/<lang>`
**Purpose**: Set user language preference

**Parameters:**
- `lang`: Language code

**Response**: Redirect to `/` with session updated

#### `POST /ask`
**Purpose**: AI chat assistant

**Request:**
```json
{
  "question": "User question text",
  "medicines": [/* medicine objects */],
  "language": "Hindi"
}
```

**Response:**
```json
{
  "answer": "AI response in target language"
}
```

#### `POST /speak`
**Purpose**: Generate TTS for specific text

**Request:**
```json
{
  "text": "Text to speak",
  "language": "Hindi",
  "purpose": "Medicine purpose (optional)",
  "purpose_label": "Purpose label translation"
}
```

**Response:**
```json
{
  "audio_url": "/static/audio/chat_{uuid}.mp3"
}
```

### 4.2 External API Integration

#### Google Gemini API

**Endpoint**: `client.models.generate_content()`

**Request Structure:**
```python
{
  "model": "gemini-2.0-flash",
  "contents": [
    "prompt_text",
    Part.from_bytes(data=image_data, mime_type="image/jpeg")
  ]
}
```

**Response Structure:**
```json
{
  "english": [
    {
      "name": "Medicine Name",
      "purpose": "Simple purpose",
      "dosage": "1-0-1",
      "visual_timing": "☀️ -- 🌙",
      "timing": "After food",
      "frequency": "After food",
      "duration": "5 days",
      "warnings": "Take with water",
      "precautions": "Take with water",
      "generic_alternative": "Generic name"
    }
  ],
  "translated": [/* same structure, translated */],
  "dangerous_combinations": [
    {
      "medicines": "Medicine A + Medicine B",
      "risk": "English explanation",
      "risk_translated": "Translated explanation",
      "severity": "high|medium"
    }
  ]
}
```

**Error Handling:**
- 429 (Rate Limit): Linear backoff, retry 3 times, fallback to next model
- 404 (Model Not Found): Immediate fallback to next model
- 503 (Service Unavailable): Exponential backoff, retry 3 times
- Generic errors: Retry with backoff, then fallback

## 5. UI/UX Design

### 5.1 Design System

**Color Palette:**
```css
--bg: #faf8f5           /* Warm background */
--text: #1a1a1a         /* Primary text */
--accent: #8b1a2b       /* Brand red */
--secondary: #a52a2a    /* Secondary red */
--card-bg: #ffffff      /* Card background */
--border: #d4c5b9       /* Border color */
```

**Typography:**
- Headings: Merriweather (serif, bold)
- Body: Manrope (sans-serif)
- Font sizes: Mobile-first (1rem base)

**Spacing:**
- Minimum touch target: 48px (WCAG compliance)
- Card padding: 16-24px
- Section margins: 20-40px

### 5.2 Component Design

#### Medicine Card
```
┌─────────────────────────────────────┐
│ Medicine 1                    🔊    │ ← Header (accent color)
├─────────────────────────────────────┤
│ 💰 Generic Alternative              │ ← Cost savings (green)
├─────────────────────────────────────┤
│         Dosage: 1-0-1               │ ← Large, centered
├─────────────────────────────────────┤
│ 🕒 Frequency: After food            │
│ 📅 Duration: 5 days                 │
│ Purpose: For fever                  │
├─────────────────────────────────────┤
│ ⚠️ CAUTION                          │ ← Warning box (amber)
│ Take with water                     │
└─────────────────────────────────────┘
```

#### Schedule View
```
┌─────────────────────────────────────┐
│     📅 DAILY SCHEDULE               │
├─────────────────────────────────────┤
│ ☀️ MORNING              🔔 Set Alarm│
│ • Medicine A (1 tablet)             │
│   After food                        │
├─────────────────────────────────────┤
│ 🌤️ AFTERNOON            🔔 Set Alarm│
│ (No medicines)                      │
├─────────────────────────────────────┤
│ 🌙 NIGHT                🔔 Set Alarm│
│ • Medicine A (1 tablet)             │
│   After food                        │
└─────────────────────────────────────┘
```

#### History Card
```
┌─────────────────────────────────────┐
│ 2024-02-15 14:30 · Hindi    [Myself]│
│ Medicine A, Medicine B, Medicine C  │
│ [View] [Share] [Delete]             │
└─────────────────────────────────────┘
```

### 5.3 Responsive Design

**Breakpoints:**
- Mobile: < 768px (primary target)
- Tablet: 768px - 1024px
- Desktop: > 1024px

**Mobile-First Approach:**
- Single column layout
- Full-width cards
- Bottom navigation
- Large touch targets
- Minimal text input

**Accessibility Features:**
- High contrast colors
- Icon + text labels
- Voice input support
- Screen reader compatible
- Keyboard navigation

## 6. Security Design

### 6.1 Authentication & Authorization

**Session Management:**
- Flask session with random secret key
- Session invalidation on server restart
- No persistent user accounts
- Language preference stored in session

**Data Privacy:**
- No PII storage on server
- Images stored temporarily
- Audio files stored temporarily
- Client-side history only
- No analytics or tracking

### 6.2 Input Validation

**Image Upload:**
- File type validation (JPEG/JPG only)
- Client-side quality checks
- Server-side file size limits
- UUID-based filenames (prevent path traversal)

**API Input:**
- JSON schema validation
- SQL injection prevention (no database)
- XSS prevention (template escaping)
- CSRF protection (Flask built-in)

### 6.3 API Security

**Environment Variables:**
- `GOOGLE_API_KEY` stored securely
- No hardcoded credentials
- API key rotation support

**Rate Limiting:**
- Handled by Google Gemini API
- Retry logic with backoff
- Model fallback strategy

## 7. Performance Optimization

### 7.1 Image Processing

**Optimization Techniques:**
- Resize to 1024x1024 before upload
- JPEG compression (85% quality)
- Thumbnail generation
- Memory cleanup after processing

**Performance Targets:**
- Image upload: < 2 seconds
- AI processing: < 10 seconds
- Total time: < 15 seconds

### 7.2 Frontend Optimization

**Loading Strategy:**
- Lazy loading for images
- Async script loading
- Minimal CSS (inline critical)
- Service worker caching (PWA)

**Bundle Size:**
- No external JavaScript libraries
- Vanilla JS only
- Inline CSS for critical path
- Font subsetting

### 7.3 Caching Strategy

**Browser Caching:**
- Static assets: 1 year
- Audio files: 1 hour
- HTML: No cache

**Service Worker:**
- Cache static assets
- Offline fallback page
- Background sync for uploads

## 8. Error Handling

### 8.1 Client-Side Errors

**Image Quality Issues:**
```
Error Type: blurry
Display: "📸 Photo is blurry. Please hold steady and try again."
Action: Show retry button, suggest manual input
```

```
Error Type: dark
Display: "📸 Photo is too dark. Try in better light."
Action: Show retry button, suggest manual input
```

**Network Errors:**
```
Error Type: offline
Display: "No internet connection. Please try again."
Action: Queue for background sync (PWA)
```

### 8.2 Server-Side Errors

**AI Processing Errors:**
```
Error Type: api_error
Display: "🔄 Could not read the prescription. Please try again."
Action: Show retry button, log error details
```

```
Error Type: quota_exceeded
Display: "Server is busy. Please try again in a minute."
Action: Show retry button, suggest manual input
```

**Parsing Errors:**
```
Error Type: parse_error
Display: "Could not understand prescription format."
Action: Show retry button, suggest manual input
```

### 8.3 Fallback Mechanisms

**AI Model Fallback:**
1. Try `gemini-2.0-flash` (3 retries)
2. Try `gemini-1.5-flash` (3 retries)
3. Try `gemini-1.5-pro` (3 retries)
4. Show error message with manual input option

**TTS Fallback:**
1. Try server-side gTTS
2. Fall back to Web Speech API
3. Show text-only if both fail

**Manual Input Fallback:**
- Chat interface always available
- User can type medicine name
- AI provides information without OCR

## 9. Internationalization (i18n)

### 9.1 Translation Architecture

**Translation Storage:**
```python
TRANSLATIONS = {
    "English": { "key": "value", ... },
    "Hindi": { "key": "मान", ... },
    # ... other languages
}
```

**Translation Keys:**
- UI labels: `hero_title`, `upload_title`, etc.
- Button text: `start_btn`, `process_btn`, etc.
- Error messages: `error_blurry`, `error_dark`, etc.
- Medicine fields: `medicine_label`, `dosage_label`, etc.

### 9.2 Language Support

**Supported Languages:**
1. English (default)
2. Hindi (हिंदी)
3. Kannada (ಕನ್ನಡ)
4. Tamil (தமிழ்)
5. Telugu (తెలుగు)
6. Malayalam (മലയാളം)

**Translation Scope:**
- Complete UI translation
- Medicine details translation
- Audio synthesis in native language
- Chat responses in native language
- Error messages in native language

**Language Detection:**
- User selection on first visit
- Stored in session
- Persistent across visits
- Can be changed anytime

### 9.3 TTS Language Mapping

```python
lang_code_map = {
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "English": "en"
}
```

## 10. Progressive Web App (PWA)

### 10.1 Manifest Configuration

```json
{
  "name": "Prescription AI Assistant",
  "short_name": "Prescription AI",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#991b1b",
  "icons": [
    { "src": "icon-192.png", "sizes": "192x192" },
    { "src": "icon-512.png", "sizes": "512x512" }
  ]
}
```

### 10.2 Service Worker Strategy

**Caching Strategy:**
- Static assets: Cache-first
- API calls: Network-first
- Images: Cache-first with expiration
- Audio: Cache-first with expiration

**Offline Support:**
- Cached UI available offline
- Show offline message for API calls
- Queue uploads for background sync
- Cached history accessible offline

### 10.3 Installation Prompts

**Install Triggers:**
- After first successful scan
- After 3 visits
- Manual install button in settings

**Install Benefits:**
- Home screen icon
- Fullscreen experience
- Faster loading
- Offline access to history

## 11. Testing Strategy

### 11.1 Unit Testing

**Backend Tests:**
- Image processing functions
- JSON parsing logic
- Translation functions
- Error handling

**Frontend Tests:**
- Form validation
- Image quality checks
- localStorage operations
- Profile management

### 11.2 Integration Testing

**API Integration:**
- Gemini API calls
- gTTS generation
- Error handling
- Retry logic

**End-to-End:**
- Complete prescription flow
- Chat interaction
- History management
- Sharing functionality

### 11.3 User Acceptance Testing

**Test Scenarios:**
1. First-time user flow
2. Prescription upload and analysis
3. Audio playback
4. Chat interaction
5. History management
6. Profile switching
7. Language switching
8. Sharing on WhatsApp
9. Offline usage
10. Error recovery

**Test Devices:**
- Android phones (various screen sizes)
- iOS devices
- Tablets
- Desktop browsers

## 12. Deployment Architecture

### 12.1 Heroku Deployment

**Configuration:**
```
Procfile: web: gunicorn app:app --bind 0.0.0.0:$PORT
Runtime: Python 3.8+
Buildpacks: Python, Tesseract OCR
```

**Environment Variables:**
```
GOOGLE_API_KEY=<api_key>
PORT=<auto_assigned>
```

**Scaling:**
- Horizontal scaling via dynos
- Stateless design enables easy scaling
- No database dependencies

### 12.2 File Storage

**Temporary Storage:**
- `uploads/` and `static/audio/` on dyno filesystem
- Files cleared on dyno restart
- Consider cloud storage for production (S3, GCS)

**Persistent Storage:**
- Client-side localStorage only
- No server-side persistence required

### 12.3 Monitoring & Logging

**Application Logs:**
- Flask debug logs
- API error logs
- Performance metrics
- User error reports

**Monitoring:**
- Heroku metrics dashboard
- API quota usage
- Error rates
- Response times

## 13. Future Enhancements

### 13.1 Planned Features

**Phase 2:**
- User authentication
- Cloud storage for prescriptions
- Medicine reminder notifications
- Pharmacy integration
- Doctor consultation booking

**Phase 3:**
- Offline OCR capability
- Additional language support
- Medicine interaction database
- Refill reminders
- Family member profiles with separate histories

### 13.2 Technical Improvements

**Performance:**
- CDN for static assets
- Image optimization pipeline
- Lazy loading for history
- Pagination for large histories

**Features:**
- Voice-only mode for low-literacy users
- SMS integration for feature phones
- Barcode scanning for medicines
- Dosage calculator
- Medicine price comparison

### 13.3 Scalability Considerations

**Database Migration:**
- PostgreSQL for user accounts
- Redis for session storage
- S3 for file storage
- CloudFront for CDN

**Microservices:**
- Separate OCR service
- Separate TTS service
- Separate AI service
- API gateway

## 14. Compliance & Regulations

### 14.1 Medical Disclaimer

**Required Disclaimers:**
- Not a substitute for medical advice
- Consult doctor for medical decisions
- No diagnosis capability
- Information accuracy not guaranteed

**Display Requirements:**
- Visible on every page
- Clear and prominent
- Multiple languages
- User acknowledgment

### 14.2 Data Privacy

**GDPR Compliance:**
- No personal data collection
- User consent for localStorage
- Right to delete data
- Data portability

**HIPAA Considerations:**
- No PHI storage on server
- Client-side encryption option
- Secure transmission (HTTPS)
- Audit logging

### 14.3 Accessibility Standards

**WCAG 2.1 Level AA:**
- Minimum touch target: 48px
- Color contrast ratio: 4.5:1
- Keyboard navigation
- Screen reader support
- Alternative text for images
- Captions for audio

## 15. Maintenance & Support

### 15.1 Maintenance Schedule

**Regular Updates:**
- Security patches: Weekly
- Dependency updates: Monthly
- Feature releases: Quarterly
- Major versions: Annually

**Monitoring:**
- API quota usage: Daily
- Error rates: Real-time
- Performance metrics: Daily
- User feedback: Weekly

### 15.2 Support Channels

**User Support:**
- In-app help documentation
- FAQ section
- Email support
- Community forum

**Technical Support:**
- GitHub issues
- Developer documentation
- API documentation
- Integration guides

### 15.3 Backup & Recovery

**Data Backup:**
- No server-side data to backup
- User responsible for localStorage
- Export functionality for user data
- Cloud sync option (future)

**Disaster Recovery:**
- Stateless design enables quick recovery
- Redeploy from Git repository
- Environment variables from secure storage
- No data loss (client-side storage)
