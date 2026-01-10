import os
import wave
from deep_translator import GoogleTranslator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_OUTPUT_DIR = os.path.join(BASE_DIR, 'output_audio')
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

def process_tts(text, target_lang='id'):
    """
    Versi Bypass/Dummy:
    Tetap menerjemahkan teks agar terlihat dinamis, 
    tapi audionya SELALU mengembalikan 'Kore.wav'.
    """
    try:
        # Validasi Input
        if not text or not text.strip():
            return {"error": "Text kosong"}
        
        text = text.strip()

        # Translate Text
        print(f"Menerjemahkan ke {target_lang}...")
        try:
            translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        except Exception as e:
            translated_text = text 
            print(f"Gagal translate (mode offline): {e}")

        # Bypass Audio Generation
        print("Generate Audio: MENGGUNAKAN FILE STATIS (Kore.wav)...")

        # File statis audio dummy
        static_filename = "Kore.wav"
        static_filepath = os.path.join(AUDIO_OUTPUT_DIR, static_filename)

        if not os.path.exists(static_filepath):
            return {"error": f"File '{static_filename}' tidak ditemukan di folder output_audio! Silakan masukkan file audio dummy."}

        return {
            "original_text": text,
            "translated_text": translated_text,
            "audio_filename": static_filename  # Selalu return Kore.wav
        }
        
    except Exception as e:
        print(f"Error TTS: {e}")
        return {"error": str(e)}

def get_supported_languages():
    # Return list bahasa manual
    return [
        {"name": "Indonesia", "code": "id"}, 
        {"name": "Inggris", "code": "en"},
        {"name": "Jepang", "code": "ja"},
        {"name": "Korea", "code": "ko"}
    ]