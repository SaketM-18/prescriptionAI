from flask import Flask, render_template, request, make_response, redirect, url_for
from pipeline import run_pipeline
from gtts import gTTS
import json, os, uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
AUDIO_FOLDER = "static/audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# UI Translations
TRANSLATIONS = {
    "English": {
        "hero_title": "DECODE<br><span>YOUR HEALTH</span>",
        "hero_desc": "Advanced AI prescription analysis. Accuracy meets simplicity. Upload your prescription and let our engine handle the rest.",
        "start_btn": "START ANALYSIS",
        "upload_title": "UPLOAD DOCUMENT",
        "lang_label": "PRESCRIPTION LANGUAGE",
        "file_label": "PHOTO OF PRESCRIPTION",
        "process_btn": "PROCESS PRESCRIPTION",
        "analyzing": "ANALYZING SCRIPT...",
        "report_title": "PRESCRIPTION GUIDE",
        "listen_btn": "🔊 LISTEN TO INSTRUCTIONS",
        "medicine_label": "MEDICINE",
        "dosage_label": "DOSAGE",
        "frequency_label": "WHEN TO TAKE",
        "purpose_label": "PURPOSE",
        "caution_label": "⚠️ CAUTION",
        "share_btn": "SHARE ON WHATSAPP",
        "scan_btn": "SCAN ANOTHER",
        "brand_tagline": "AI POWERED PRECISION"
    },
    "Hindi": {
        "hero_title": "अपनी सेहत<br><span>को समझें</span>",
        "hero_desc": "उन्नत एआई नुस्खा विश्लेषण। अपना नुस्खा अपलोड करें और बाकी हम पर छोड़ दें।",
        "start_btn": "जांच शुरू करें",
        "upload_title": "दस्तावेज़ अपलोड करें",
        "lang_label": "नुस्खे की भाषा",
        "file_label": "नुस्खे की फोटो",
        "process_btn": "प्रक्रिया शुरू करें",
        "analyzing": "विश्लेषण चल रहा है...",
        "report_title": "दवा गाइड",
        "listen_btn": "🔊 निर्देश सुनें",
        "medicine_label": "दवा",
        "dosage_label": "खुराक",
        "frequency_label": "कब लेनी है",
        "purpose_label": "उद्देश्य",
        "caution_label": "⚠️ सावधानी",
        "share_btn": "व्हाट्सएप पर भेजें",
        "scan_btn": "दूसरा स्कैन करें",
        "brand_tagline": "एआई आधारित सटीकता"
    },
    "Kannada": {
        "hero_title": "ನಿಮ್ಮ ಆರೋಗ್ಯವನ್ನು<br><span>ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ</span>",
        "hero_desc": "ಸುಧಾರಿತ AI ಪ್ರಿಸ್ಕ್ರಿಪ್ಷನ್ ವಿಶ್ಲೇಷಣೆ. ನಿಮ್ಮ ಪ್ರಿಸ್ಕ್ರಿಪ್ಷನ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
        "start_btn": "ವಿಶ್ಲೇಷಣೆ ಪ್ರಾರಂಭಿಸಿ",
        "upload_title": "ದಾಖಲೆ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "lang_label": "ಪ್ರಿಸ್ಕ್ರಿಪ್ಷನ್ ಭಾಷೆ",
        "file_label": "ಪ್ರಿಸ್ಕ್ರಿಪ್ಷನ್ ಫೋಟೋ",
        "process_btn": "ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಿ",
        "analyzing": "ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...",
        "report_title": "ಔಷಧಿ ಮಾರ್ಗದರ್ಶಿ",
        "listen_btn": "🔊 ಸೂಚನೆಗಳನ್ನು ಆಲಿಸಿ",
        "medicine_label": "ಔಷಧಿ",
        "dosage_label": "ಡೋಸೇಜ್",
        "frequency_label": "ಯಾವಾಗ ತೆಗೆದುಕೊಳ್ಳಬೇಕು",
        "purpose_label": "ಉದ್ದೇಶ",
        "caution_label": "⚠️ ಎಚ್ಚರಿಕೆ",
        "share_btn": "ವಾಟ್ಸಾಪ್‌ನಲ್ಲಿ ಹಂಚಿಕೊಳ್ಳಿ",
        "scan_btn": "ಮತ್ತೊಂದು ಸ್ಕ್ಯಾನ್ ಮಾಡಿ",
        "brand_tagline": "AI ಚಾಲಿತ ನಿಖರತೆ"
    },
    "Tamil": {
        "hero_title": "உங்கள் ஆரோக்கியத்தைப்<br><span>புரிந்துகொள்ளுங்கள்</span>",
        "hero_desc": "மேம்பட்ட AI மருந்துச் சீட்டு பகுப்பாய்வு. உங்கள் மருந்துச் சீட்டைப் பதிவேற்றவும்.",
        "start_btn": "பகுப்பாய்வைத் தொடங்கு",
        "upload_title": "ஆவணத்தைப் பதிவேற்றவும்",
        "lang_label": "மொழி",
        "file_label": "புகைப்படம்",
        "process_btn": "செயலாக்கு",
        "analyzing": "பகுப்பாய்வு செய்கிறது...",
        "report_title": "மருந்து வழிகாட்டி",
        "listen_btn": "🔊 வழிமுறைகளைக் கேளுங்கள்",
        "medicine_label": "மருந்து",
        "dosage_label": "அளவு",
        "frequency_label": "எப்போது எடுக்க வேண்டும்",
        "purpose_label": "நோக்கம்",
        "caution_label": "⚠️ எச்சரிக்கை",
        "share_btn": "வாட்ஸ்அப்பில் பகிரவும்",
        "scan_btn": "மற்றொன்றை ஸ்கேன் செய்",
        "brand_tagline": "AI துல்லியம்"
    },
    "Telugu": {
        "hero_title": "మీ ఆరోగ్యాన్ని<br><span>అర్థం చేసుకోండి</span>",
        "hero_desc": "అధునాతన AI ప్రిస్క్రిప్షన్ విశ్లేషణ. మీ ప్రిస్క్రిప్షన్‌ను అప్‌లోడ్ చేయండి.",
        "start_btn": "విశ్లేషణ ప్రారంభించు",
        "upload_title": "పత్రం అప్‌లోడ్ చేయండి",
        "lang_label": "భాష",
        "file_label": "ఫోటో",
        "process_btn": "ప్రాసెస్ చేయండి",
        "analyzing": "విశ్లేషించబడుతోంది...",
        "report_title": "మందుల గైడ్",
        "listen_btn": "🔊 సూచనలను వినండి",
        "medicine_label": "మందు",
        "dosage_label": "మోతాదు",
        "frequency_label": "ఎప్పుడు తీసుకోవాలి",
        "purpose_label": "ఉద్దేశ్యం",
        "caution_label": "⚠️ హెచ్చరిక",
        "share_btn": "వాట్సాప్‌లో షేర్ చేయండి",
        "scan_btn": "మరొకటి స్కాన్ చేయండి",
        "brand_tagline": "AI ఆధారిత ఖచ్చితత్వం"
    },
    "Malayalam": {
        "hero_title": "നിങ്ങളുടെ ആരോഗ്യം<br><span>മനസ്സിലാക്കുക</span>",
        "hero_desc": "വിപുലമായ AI കുറിപ്പടി വിശകലനം. നിങ്ങളുടെ കുറിപ്പടി അപ്‌ലോഡ് ചെയ്യുക.",
        "start_btn": "വിശകലനം തുടങ്ങുക",
        "upload_title": "രേഖ അപ്‌ലോഡ് ചെയ്യുക",
        "lang_label": "ഭാഷ",
        "file_label": "ഫോട്ടോ",
        "process_btn": "പ്രോസസ്സ് ചെയ്യുക",
        "analyzing": "വിശകലനം ചെയ്യുന്നു...",
        "report_title": "മരുന്ന് ഗൈഡ്",
        "listen_btn": "🔊 നിർദ്ദേശങ്ങൾ കേൾക്കുക",
        "medicine_label": "മരുന്ന്",
        "dosage_label": "അളവ്",
        "frequency_label": "എപ്പോൾ കഴിക്കണം",
        "purpose_label": "ഉദ്ദേശ്യം",
        "caution_label": "⚠️ മുന്നറിയിപ്പ്",
        "share_btn": "വാട്ട്‌സ്ആപ്പിൽ പങ്കിടുക",
        "scan_btn": "മറ്റൊന്ന് സ്കാൻ ചെയ്യുക",
        "brand_tagline": "AI പവർഡ്"
    }
}

@app.route("/", methods=["GET", "POST"])
def index():
    user_lang = request.cookies.get("user_lang")
    
    # If no language is set, render the Language Wall
    if not user_lang:
        return render_template("language.html")
    
    # Default to English if cookie is invalid
    if user_lang not in TRANSLATIONS:
        user_lang = "English"
        
    texts = TRANSLATIONS[user_lang]
    english = None
    translated = None
    audio_path = None

    if request.method == "POST":
        language = request.form.get("language")
        # Fallback if language not in form, use user_lang or default
        if not language:
            language = user_lang

        image = request.files.get("image")
        if image:
            filename = f"{uuid.uuid4()}.jpg"
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(save_path)
            
            # 1. Run Pipeline (Returns JSON String)
            raw_response = run_pipeline(save_path, language)
            
            try:
                # 2. Parse JSON
                data = json.loads(raw_response)
                english = data.get("english", [])
                translated = data.get("translated", [])

                # 3. Generate Audio
                audio_text = f"Prescription Guide in {language}. "
                
                # Determine which list to read (translated if available, else english)
                med_list = translated if translated else english
                
                for med in med_list:
                    # Robust extraction with defaults
                    name = med.get('medicine_name') or med.get('name') or "Medicine"
                    purpose = med.get('purpose') or "As prescribed"
                    dosage = med.get('dosage') or "As directed"
                    timing = med.get('frequency') or med.get('timing') or ""
                    
                    audio_text += f"{name}. {purpose}. Dosage: {dosage}. {timing}. "

                # Map Language to GTTS Code
                lang_code_map = {
                    "Hindi": "hi",
                    "Tamil": "ta",
                    "Telugu": "te",
                    "Kannada": "kn",
                    "Malayalam": "ml",
                    "English": "en"
                }

                tts = gTTS(text=audio_text, lang=lang_code_map.get(language, "en"))
                audio_filename = f"{uuid.uuid4()}.mp3"
                tts.save(os.path.join(AUDIO_FOLDER, audio_filename))
                audio_path = f"audio/{audio_filename}"
            
            except Exception as e:
                print(f"Error parsing AI response: {e}")
                # Fallback: maintain None for english/translated to show error or empty

    return render_template(
        "index.html",
        english=english,
        translated=translated,
        language=user_lang,
        audio_path=audio_path,
        texts=texts
    )

@app.route("/set_language/<lang>")
def set_language(lang):
    if lang in TRANSLATIONS:
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie("user_lang", lang, max_age=60*60*24*365) # 1 year
        return resp
    return redirect(url_for("index"))

@app.route("/reset_language")
def reset_language():
    resp = make_response(redirect(url_for("index")))
    resp.set_cookie("user_lang", "", expires=0)
    return resp

if __name__ == "__main__":
    app.run(debug=True)
