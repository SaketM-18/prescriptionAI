from flask import Flask, render_template, request, make_response, redirect, url_for, session, jsonify
from pipeline import run_pipeline, client
import time
from gtts import gTTS
import json, os, uuid

app = Flask(__name__)
app.secret_key = os.urandom(24) # Generates new key on every restart -> Invalidates all old sessions

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
        "duration_label": "FOR HOW LONG",
        "purpose_label": "PURPOSE",
        "caution_label": "⚠️ CAUTION",
        "share_btn": "SHARE ON WHATSAPP",
        "scan_btn": "SCAN ANOTHER",
        "brand_tagline": "AI POWERED PRECISION",
        "no_file": "No file chosen",
        "choose_file": "Choose File",
        "change_file": "Change File",
        "my_medicines": "📋 MY MEDICINES",
        "no_history": "No prescriptions saved yet. Upload your first one!",
        "delete_btn": "Delete",
        "date_label": "Date",
        "history_title": "SAVED PRESCRIPTIONS",
        "view_btn": "View",
        "close_btn": "Close",
        "share_lang_title": "Share in which language?",
        "camera_btn": "Take Photo",
        "generic_label": "Cheaper Option: ",
        "chat_title": "Medicine Assistant",
        "chat_subtitle": "Ask about your medicines",
        "chat_welcome": "Hello! 👋 Ask me anything about your medicines. Tap the mic to speak!",
        "chat_placeholder": "Type or tap mic...",
        "schedule_title": "📅 DAILY SCHEDULE",
        "morning": "☀️ MORNING",
        "afternoon": "🌤️ AFTERNOON",
        "night": "🌙 NIGHT",
        "set_alarm": "Set Alarm",
        "tablet": "tablet(s)",
        "interaction_title": "⚠️ Dangerous Combinations",
        "interaction_advice": "👨‍⚕️ Please consult your doctor about these combinations"
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
        "duration_label": "कितने दिन",
        "purpose_label": "उद्देश्य",
        "caution_label": "⚠️ सावधानी",
        "share_btn": "व्हाट्सएप पर भेजें",
        "scan_btn": "दूसरा स्कैन करें",
        "brand_tagline": "एआई आधारित सटीकता",
        "no_file": "कोई फाइल नहीं चुनी गई",
        "choose_file": "फाइल चुनें",
        "change_file": "फाइल बदलें",
        "my_medicines": "📋 मेरी दवाइयाँ",
        "no_history": "अभी तक कोई नुस्खा सहेजा नहीं गया। अपना पहला अपलोड करें!",
        "delete_btn": "हटाएं",
        "date_label": "तारीख",
        "history_title": "सहेजे गए नुस्खे",
        "view_btn": "देखें",
        "close_btn": "बंद करें",
        "share_lang_title": "किस भाषा में भेजें?",
        "camera_btn": "फोटो लें",
        "generic_label": "सस्ता विकल्प: ",
        "chat_title": "दवाई सहायक",
        "chat_subtitle": "अपनी दवाइयों के बारे में पूछें",
        "chat_welcome": "नमस्ते! 👋 अपनी दवाइयों के बारे में कुछ भी पूछें। माइक दबाकर बोलें!",
        "chat_placeholder": "टाइप करें या माइक दबाएं...",
        "schedule_title": "📅 दैनिक समय सारिणी",
        "morning": "☀️ सुबह",
        "afternoon": "🌤️ दोपहर",
        "night": "🌙 रात",
        "set_alarm": "अलार्म सेट करें",
        "tablet": "गोली",
        "interaction_title": "⚠️ खतरनाक संयोजन",
        "interaction_advice": "👨‍⚕️ कृपया इन संयोजनों के बारे में अपने डॉक्टर से सलाह लें"
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
        "duration_label": "ಎಷ್ಟು ದಿನಗಳು",
        "purpose_label": "ಉದ್ದೇಶ",
        "caution_label": "⚠️ ಎಚ್ಚರಿಕೆ",
        "share_btn": "ವಾಟ್ಸಾಪ್‌ನಲ್ಲಿ ಹಂಚಿಕೊಳ್ಳಿ",
        "scan_btn": "ಮತ್ತೊಂದು ಸ್ಕ್ಯಾನ್ ಮಾಡಿ",
        "brand_tagline": "AI ಚಾಲಿತ ನಿಖರತೆ",
        "no_file": "ಯಾವುದೇ ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿಲ್ಲ",
        "choose_file": "ಫೈಲ್ ಆಯ್ಕೆಮಾಡಿ",
        "change_file": "ಫೈಲ್ ಬದಲಾಯಿಸಿ",
        "my_medicines": "📋 ನನ್ನ ಔಷಧಿಗಳು",
        "no_history": "ಯಾವುದೇ ಪ್ರಿಸ್ಕ್ರಿಪ್ಷನ್ ಉಳಿಸಿಲ್ಲ. ನಿಮ್ಮ ಮೊದಲನೆಯದನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ!",
        "delete_btn": "ಅಳಿಸಿ",
        "date_label": "ದಿನಾಂಕ",
        "history_title": "ಉಳಿಸಿದ ಪ್ರಿಸ್ಕ್ರಿಪ್ಷನ್‌ಗಳು",
        "view_btn": "ನೋಡಿ",
        "close_btn": "ಮುಚ್ಚಿ",
        "share_lang_title": "ಯಾವ ಭಾಷೆಯಲ್ಲಿ ಹಂಚಿಕೊಳ್ಳಬೇಕು?",
        "schedule_title": "📅 ದೈನಂದಿನ ವೇಳಾಪಟ್ಟಿ",
        "morning": "☀️ ಬೆಳಿಗ್ಗೆ",
        "afternoon": "🌤️ ಮಧ್ಯಾಹ್ನ",
        "night": "🌙 ರಾತ್ರಿ",
        "set_alarm": "ಅಲಾರಾಂ ಹೊಂದಿಸಿ",
        "tablet": "ಮಾತ್ರೆ",
        "camera_btn": "ಫೋಟೋ ತೆಗೆದುಕೊಳ್ಳಿ",
        "generic_label": "ಅಗ್ಗದ ಪರ್ಯಾಯ: ",
        "chat_title": "ಔಷಧ ಸಹಾಯಕ",
        "chat_subtitle": "ನಿಮ್ಮ ಔಷಧಗಳ ಬಗ್ಗೆ ಕೇಳಿ",
        "chat_welcome": "ನಮಸ್ಕಾರ! 👋 ನಿಮ್ಮ ಔಷಧಗಳ ಬಗ್ಗೆ ಏನಾದರೂ ಕೇಳಿ. ಮೈಕ್ ಒತ್ತಿ ಮಾತನಾಡಿ!",
        "chat_placeholder": "ಟೈಪ್ ಮಾಡಿ ಅಥವಾ ಮೈಕ್ ಒತ್ತಿ...",
        "interaction_title": "⚠️ ಅಪಾಯಕಾರಿ ಸಂಯೋಜನೆಗಳು",
        "interaction_advice": "👨‍⚕️ ದಯವಿಟ್ಟು ಈ ಸಂಯೋಜನೆಗಳ ಬಗ್ಗೆ ನಿಮ್ಮ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ"
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
        "duration_label": "எத்தனை நாட்கள்",
        "purpose_label": "நோக்கம்",
        "caution_label": "⚠️ எச்சரிக்கை",
        "share_btn": "வாட்ஸ்அப்பில் பகிரவும்",
        "scan_btn": "மற்றொன்றை ஸ்கேன் செய்",
        "brand_tagline": "AI துல்லியம்",
        "no_file": "கோப்பு தேர்ந்தெடுக்கப்படவில்லை",
        "choose_file": "கோப்பைத் தேர்ந்தெடுக்கவும்",
        "change_file": "கோப்பை மாற்றவும்",
        "my_medicines": "📋 எனது மருந்துகள்",
        "no_history": "இதுவரை மருந்துச் சீட்டு சேமிக்கப்படவில்லை. முதலில் பதிவேற்றவும்!",
        "delete_btn": "நீக்கு",
        "date_label": "தேதி",
        "history_title": "சேமித்த மருந்துச் சீட்டுகள்",
        "view_btn": "பார்க்க",
        "close_btn": "மூடு",
        "share_lang_title": "எந்த மொழியில் பகிர வேண்டும்?",
        "schedule_title": "📅 தினசரி அட்டவணை",
        "morning": "☀️ காலை",
        "afternoon": "🌤️ மதியம்",
        "night": "🌙 இரவு",
        "set_alarm": "அலாரம் அமைக்கவும்",
        "tablet": "மாத்திரை",
        "camera_btn": "புகைப்படம் எடு",
        "generic_label": "மலிவான மாற்று: ",
        "chat_title": "மருந்து உதவியாளர்",
        "chat_subtitle": "உங்கள் மருந்துகள் பற்றி கேளுங்கள்",
        "chat_welcome": "வணக்கம்! 👋 உங்கள் மருந்துகள் பற்றி எது வேண்டுமானாலும் கேளுங்கள். மைக் தட்டி பேசுங்கள்!",
        "chat_placeholder": "டைப் செய்யவும் அல்லது மைக் தட்டவும்...",
        "interaction_title": "⚠️ ஆபத்தான சேர்க்கைகள்",
        "interaction_advice": "👨‍⚕️ இந்த சேர்க்கைகள் பற்றி உங்கள் மருத்துவரிடம் ஆலோசிக்கவும்"
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
        "duration_label": "ఎన్ని రోజులు",
        "purpose_label": "ఉద్దేశ్యం",
        "caution_label": "⚠️ హెచ్చరిక",
        "share_btn": "వాట్సాప్‌లో షేర్ చేయండి",
        "scan_btn": "మరొకటి స్కాన్ చేయండి",
        "brand_tagline": "AI ఆధారిత ఖచ్చితత్వం",
        "no_file": "ఏ ఫైల్ ఎంపిక చేయబడలేదు",
        "choose_file": "ఫైల్ ఎంచుకోండి",
        "change_file": "ఫైల్ మార్చండి",
        "my_medicines": "📋 నా మందులు",
        "no_history": "ఇంకా ప్రిస్క్రిప్షన్ సేవ్ చేయబడలేదు. మీ మొదటిదాన్ని అప్‌లోడ్ చేయండి!",
        "delete_btn": "తొలగించు",
        "date_label": "తేదీ",
        "history_title": "సేవ్ చేసిన ప్రిస్క్రిప్షన్లు",
        "view_btn": "చూడండి",
        "close_btn": "మూసివేయండి",
        "share_lang_title": "ఏ భాషలో షేర్ చేయాలి?",
        "schedule_title": "📅 రోజువారీ షెడ్యూల్",
        "morning": "☀️ ఉదయం",
        "afternoon": "🌤️ మధ్యాహ్నం",
        "night": "🌙 రాత్రి",
        "set_alarm": "అలారం సెట్ చేయండి",
        "tablet": "టాబ్లెట్",
        "camera_btn": "ఫోటో తీయండి",
        "generic_label": "తక్కువ ధర ప్రత్యామ్నాయం: ",
        "chat_title": "మందు సహాయకుడు",
        "chat_subtitle": "మీ మందుల గురించి అడగండి",
        "chat_welcome": "నమస్కారం! 👋 మీ మందుల గురించి ఏదైనా అడగండి. మైక్ నొక్కి మాట్లాడండి!",
        "chat_placeholder": "టైప్ చేయండి లేదా మైక్ నొక్కండి...",
        "interaction_title": "⚠️ ప్రమాదకరమైన కలయికలు",
        "interaction_advice": "👨‍⚕️ దయచేసి ఈ కలయికల గురించి మీ వైద్యుడిని సంప్రదించండి"
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
        "duration_label": "എത്ര ദിവസം",
        "purpose_label": "ഉദ്ദേശ്യം",
        "caution_label": "⚠️ മുന്നറിയിപ്പ്",
        "share_btn": "വാട്ട്‌സ്ആപ്പിൽ പങ്കിടുക",
        "scan_btn": "മറ്റൊന്ന് സ്കാൻ ചെയ്യുക",
        "brand_tagline": "AI പവർഡ്",
        "no_file": "ഫയലുകളൊന്നും തിരഞ്ഞെടുത്തിട്ടില്ല",
        "choose_file": "ഫയൽ തിരഞ്ഞെടുക്കുക",
        "change_file": "ഫയൽ മാറ്റുക",
        "my_medicines": "📋 എന്റെ മരുന്നുകൾ",
        "no_history": "ഇതുവരെ കുറിപ്പടിയൊന്നും സേവ് ചെയ്തിട്ടില്ല. ആദ്യത്തേത് അപ്‌ലോഡ് ചെയ്യുക!",
        "delete_btn": "ഇല്ലാതാക്കുക",
        "date_label": "തീയതി",
        "history_title": "സേവ് ചെയ്ത കുറിപ്പടികൾ",
        "view_btn": "കാണുക",
        "close_btn": "അടയ്ക്കുക",
        "share_lang_title": "ഏത് ഭാഷയിൽ പങ്കിടണം?",
        "schedule_title": "📅 ദിവസേനയുള്ള സമയം",
        "morning": "☀️ രാവിലെ",
        "afternoon": "🌤️ ഉച്ചയ്ക്ക്",
        "night": "🌙 രാത്രി",
        "set_alarm": "അലാറം വെക്കുക",
        "tablet": "ഗുളിക",
        "camera_btn": "ഫോട്ടോ എടുക്കൂ",
        "generic_label": "വിലകുറഞ്ഞ ബദൽ: ",
        "chat_title": "മരുന്ന് സഹായി",
        "chat_subtitle": "നിങ്ങളുടെ മരുന്നുകളെക്കുറിച്ച് ചോദിക്കൂ",
        "chat_welcome": "നമസ്കാരം! 👋 നിങ്ങളുടെ മരുന്നുകളെക്കുറിച്ച് എന്തും ചോദിക്കൂ. മൈക് അമർത്തി സംസാരിക്കൂ!",
        "chat_placeholder": "ടൈപ്പ് ചെയ്യൂ അല്ലെങ്കിൽ മൈക് അമർത്തൂ...",
        "interaction_title": "⚠️ അപകടകരമായ സംയോജനങ്ങൾ",
        "interaction_advice": "👨‍⚕️ ദയവായി ഈ സംയോജനങ്ങളെ കുറിച്ച് നിങ്ങളുടെ ഡോക്ടറോട് ചോദിക്കൂ"
    },
}

@app.route("/", methods=["GET", "POST"])
def index():
    # Use session instead of cookies for stricter lifecycle
    user_lang = session.get("user_lang")
    
    # If no language is set, render the Language Wall
    if not user_lang:
        return render_template("language.html")
    
    # Default to English if session data is invalid
    if user_lang not in TRANSLATIONS:
        user_lang = "English"
        
    texts = TRANSLATIONS[user_lang]
    english = None
    translated = None
    dangerous_combinations = []
    audio_path = None

    if request.method == "POST":
        language = request.form.get("language")
        # Fallback if language not in form, use user_lang or default
        if not language:
            language = user_lang

        image = request.files.get("image") or request.files.get("image_camera")
        if image:
            filename = f"{uuid.uuid4()}.jpg"
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(save_path)
            
            # 1. Run Pipeline (Returns JSON String)
            raw_response = run_pipeline(save_path, language)
            
            try:
                data = json.loads(raw_response)
                english = data.get("english", [])
                translated = data.get("translated", [])
                dangerous_combinations = data.get("dangerous_combinations", [])

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

                # Add interaction warnings to audio
                if dangerous_combinations:
                    audio_text += "Warning! "
                    for combo in dangerous_combinations:
                        risk_text = combo.get('risk_translated') or combo.get('risk', '')
                        meds = combo.get('medicines', '')
                        audio_text += f"{meds}: {risk_text}. "

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
        dangerous_combinations=dangerous_combinations,
        language=user_lang,
        audio_path=audio_path,
        texts=texts,
        all_translations=TRANSLATIONS
    )

@app.route("/set_language/<lang>")
def set_language(lang):
    if lang in TRANSLATIONS:
        session["user_lang"] = lang
        return redirect(url_for("index"))
    return redirect(url_for("index"))

@app.route("/reset_language")
def reset_language():
    resp = make_response(redirect(url_for("index")))
    resp.set_cookie("user_lang", "", expires=0)
    return resp

@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    question = data.get("question", "")
    medicines = data.get("medicines", [])
    language = data.get("language", "English")

    if not question:
        return jsonify({"answer": "Please ask a question."})

    # Build medicine context
    med_context = ""
    for med in medicines:
        name = med.get("medicine_name") or med.get("name") or "Medicine"
        dosage = med.get("dosage", "")
        purpose = med.get("purpose", "")
        timing = med.get("frequency") or med.get("timing", "")
        precautions = med.get("precautions", "")
        generic = med.get("generic_alternative", "")
        med_context += f"- {name}: Dosage={dosage}, Purpose={purpose}, Timing={timing}, Precautions={precautions}, Generic={generic}\n"

    prompt = f"""You are a friendly, helpful medical assistant for rural villagers.
The patient has these medicines prescribed:
{med_context}

The patient asks (in {language}): "{question}"

Rules:
1. Answer in {language} language, using very simple words a villager can understand.
2. Keep the answer short (2-3 sentences max).
3. DO NOT diagnose or prescribe new medicines.
4. If the question is unrelated to their medicines, politely say you can only help with their prescribed medicines.
5. Be warm and reassuring.

Answer:"""

    models = ["gemini-2.0-flash", "models/gemini-flash-latest", "gemini-2.0-flash-lite"]
    answer = "Sorry, all models are busy. Please try again in a minute."
    for i, model in enumerate(models):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            answer = response.text.strip()
            break
        except Exception as e:
            if ("503" in str(e) or "429" in str(e)) and i < len(models) - 1:
                print(f"Chat model {model} unavailable, trying {models[i+1]}...")
                time.sleep(2)
                continue
            answer = f"Sorry, I could not process your question. ({str(e)})"
            break

    return jsonify({"answer": answer})

@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    text = data.get("text", "")
    language = data.get("language", "English")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    lang_code_map = {
        "Hindi": "hi",
        "Tamil": "ta",
        "Telugu": "te",
        "Kannada": "kn",
        "Malayalam": "ml",
        "English": "en"
    }

    try:
        tts = gTTS(text=text, lang=lang_code_map.get(language, "en"))
        audio_filename = f"chat_{uuid.uuid4()}.mp3"
        audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
        tts.save(audio_path)
        return jsonify({"audio_url": url_for('static', filename=f"audio/{audio_filename}")})
    except Exception as e:
        print(f"TTS error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
