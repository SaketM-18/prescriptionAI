from flask import Flask, render_template, request
from pipeline import run_pipeline
from gtts import gTTS
import json, os, uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
AUDIO_FOLDER = "static/audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    english = None
    translated = None
    language = "Hindi"
    audio_path = None

    if request.method == "POST":
        file = request.files["image"]
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        language = request.form.get("language", "Hindi")

        raw = run_pipeline(path, language)

        print("\nRAW AI OUTPUT:\n", raw)

        try:
            data = json.loads(raw)
            english = data["english"]
            translated = data["translated"]

            # Generate Audio for the whole prescription explanation
            audio_text = f"Explanation in {language}. "
            for med in translated:
                audio_text += f"Medicine: {med['name']}. Purpose: {med['purpose']}. Dosage: {med['dosage']}. Timing: {med['timing']}. Duration: {med['duration']}. Warnings: {med['warnings']}. "

            # Language codes for gTTS
            lang_code_map = {
                "Hindi": "hi",
                "Tamil": "ta",
                "Telugu": "te",
                "Kannada": "kn",
                "Malayalam": "ml"
            }
            lang_code = lang_code_map.get(language, "en")

            tts = gTTS(text=audio_text, lang=lang_code, slow=False)
            audio_filename = f"audio_{uuid.uuid4().hex}.mp3"
            audio_full_path = os.path.join(AUDIO_FOLDER, audio_filename)
            tts.save(audio_full_path)
            
            audio_path = f"audio/{audio_filename}"

        except Exception as e:
            print("Error parsing or generating audio:", e)
            english = [{
                "name": "Error",
                "purpose": "Could not process prescription",
                "dosage": "",
                "timing": "",
                "duration": "",
                "warnings": str(e)
            }]
            translated = []

    return render_template(
        "index.html",
        english=english,
        translated=translated,
        language=language,
        audio_path=audio_path
    )


if __name__ == "__main__":
    app.run(debug=True)
