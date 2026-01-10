# tts_service_elevenlabs.py
import os
from deep_translator import GoogleTranslator
from elevenlabs.client import ElevenLabs

# --- KONFIGURASI ELEVENLABS ---
# API KEY
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Setup Client
client = None
if ELEVENLABS_API_KEY:
    try:
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    except Exception as e:
        print(f"Warning: ElevenLabs client gagal init. {e}")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_OUTPUT_DIR = os.path.join(BASE_DIR, 'output_audio')
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

def process_tts(text, target_lang='id'):
    global client
    
    # Cek Client
    if not client:
        return {"error": "API Key ElevenLabs tidak ditemukan atau salah konfigurasi."}

    try:
        # Validasi Input
        if not text or not text.strip():
            return {"error": "Text kosong"}
        
        text = text.strip()

        # Translate (Default id)
        if target_lang != 'id': 
             try:
                text = GoogleTranslator(source='auto', target=target_lang).translate(text)
             except Exception as e:
                return {"error": f"Gagal translate: {e}"}

        print("Generate Audio via ElevenLabs (New API)...")

        # Generate Audio
        # "Rachel": 21m00Tcm4TlvDq8ikWAM
        # "Charlie": IKne3meq5aSn9XLyUdCD
        
        audio_stream = client.text_to_speech.convert(
            text=text,
            voice_id="21m00Tcm4TlvDq8ikWAM", # ID suara Rachel
            model_id="eleven_multilingual_v2"
        )
        
        # Simpan File
        filename = f"tts_eleven_{target_lang}_{os.urandom(4).hex()}.mp3"
        filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
        
        with open(filepath, "wb") as f:
            for chunk in audio_stream:
                if chunk:
                    f.write(chunk)
        
        return {
            "original_text": text,
            "translated_text": text,
            "audio_filename": filename
        }
        
    except Exception as e:
        print(f"Error TTS ElevenLabs: {e}")
        if "quota" in str(e).lower() or "401" in str(e) or "429" in str(e):
            return {"error": "Kuota Habis atau API Key Salah."}
        return {"error": str(e)}

def get_supported_languages():
    return [{"name": "Indonesia", "code": "id"}, {"name": "Inggris", "code": "en"}]