# tts_service_edge.py
import os
import asyncio
import edge_tts
from deep_translator import GoogleTranslator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_OUTPUT_DIR = os.path.join(BASE_DIR, 'output_audio')
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

# Fungsi async untuk generate TTS dengan Edge TTS
async def _generate_edge_tts(text, filename, voice="id-ID-GadisNeural"):
    """
    Pilihan suara Indonesia:
    - id-ID-GadisNeural (Perempuan, Natural)
    - id-ID-ArdiNeural (Laki-laki, Natural)
    - en-US-JennyNeural (Inggris Perempuan)
    - en-US-GuyNeural (Inggris Laki-laki)
    - ja-JP-NanamiNeural (Jepang Perempuan)
    - ko-KR-SunHiNeural (Korea Perempuan)
    """
    filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filepath)

def process_tts(text, target_lang='id'):
    try:
        # Validasi Input
        if not text or not text.strip():
            return {"error": "Text kosong"}
        
        text = text.strip()

        # Translate Text (jika bukan id)
        if target_lang != 'id':
            print(f"Menerjemahkan ke {target_lang}...")
            text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        
        # Generate Audio via Edge TTS (Suara Natural)
        print("Generate Audio via Edge TTS...")
        
        voice = "id-ID-GadisNeural" # Default Indo Perempuan
        if target_lang == 'en':
            voice = "en-US-JennyNeural" # Inggris Perempuan
        elif target_lang == 'ja':
            voice = "ja-JP-NanamiNeural" # Jepang Perempuan
        elif target_lang == 'ko':
            voice = "ko-KR-SunHiNeural" # Korea Perempuan
            
        filename = f"tts_{target_lang}_{os.urandom(4).hex()}.mp3"
        
        asyncio.run(_generate_edge_tts(text, filename, voice))
        
        return {
            "original_text": text,
            "translated_text": text,
            "audio_filename": filename
        }
        
    except Exception as e:
        print(f"Error TTS: {e}")
        return {"error": str(e)}

def get_supported_languages():
    return [{"name": "Indonesia", "code": "id"}, {"name": "Inggris", "code": "en"}]