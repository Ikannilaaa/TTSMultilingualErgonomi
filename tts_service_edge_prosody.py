# tts_service_edge_prosody.py
import os
import re
import asyncio
import edge_tts
from deep_translator import GoogleTranslator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_OUTPUT_DIR = os.path.join(BASE_DIR, "output_audio")
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

# Helper: preset intonasi
def _intonation_preset(style: str = "neutral"):
    
    # Return: (rate, pitch, volume)
    style = (style or "neutral").lower().strip()

    presets = {
        "neutral": ("+0%", "+0Hz", "+0%"),
        "warm_friendly": ("-10%", "-3Hz", "+0%"),
        "calm": ("-15%", "-5Hz", "-5%"),     
        "energetic": ("+10%", "+2Hz", "+10%"), 
        "formal": ("-5%", "+0Hz", "+0%"), 
    }
    return presets.get(style, presets["neutral"])


def _sanitize_prosody(rate: str, pitch: str, volume: str):
    if not re.fullmatch(r"[+-]\d{1,3}%", rate or ""): rate = "+0%"
    if not re.fullmatch(r"[+-]\d{1,3}Hz", pitch or ""): pitch = "+0Hz"
    if not re.fullmatch(r"[+-]\d{1,3}%", volume or ""): volume = "+0%"
    return rate, pitch, volume

def _add_natural_pauses(text):
    if not text: return ""
    
    # Manipulasi tanda baca
    text = text.replace(".", "... ")
    text = text.replace("!", "... ")
    text = text.replace("?", "?... ")
    

    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Async generator Edge TTS
async def _generate_edge_tts(text, filename, voice="id-ID-GadisNeural", rate="+0%", pitch="+0Hz", volume="+0%"):
    filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
    rate, pitch, volume = _sanitize_prosody(rate, pitch, volume)

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume,
    )
    await communicate.save(filepath)

def process_tts(text, target_lang="id", style="warm_friendly"):
    try:
        if not text or not text.strip():
            return {"error": "Text kosong"}

        original_text = text.strip()

        # 1. Translate
        translated_text = original_text
        if target_lang != "id":
            print(f"Menerjemahkan ke {target_lang}...")
            translated_text = GoogleTranslator(source="auto", target=target_lang).translate(original_text)

        # 2. Menambah Jeda pada audio, bukan teks asli
        audio_text = _add_natural_pauses(translated_text)

        # 3. Pilih Voice
        voice = "id-ID-GadisNeural" 
        
        if target_lang == "en":
            voice = "en-US-JennyNeural"
        elif target_lang == "ja":
            voice = "ja-JP-NanamiNeural"
        elif target_lang == "ko":
            voice = "ko-KR-SunHiNeural"

        # 4. Ambil Preset
        rate, pitch, volume = _intonation_preset(style)

        filename = f"tts_{target_lang}_{os.urandom(4).hex()}.mp3"

        print(f"Generate Audio via Edge TTS... Voice: {voice}, Style: {style}")

        asyncio.run(_generate_edge_tts(audio_text, filename, voice, rate, pitch, volume))

        return {
            "original_text": original_text,
            "translated_text": translated_text,
            "audio_filename": filename,
            "voice": voice,
            "style": style
        }

    except Exception as e:
        print(f"Error TTS: {e}")
        return {"error": str(e)}


def get_supported_languages():
    return [
        {"name": "Indonesia", "code": "id"},
        {"name": "Inggris", "code": "en"},
        {"name": "Jepang", "code": "ja"},
        {"name": "Korea", "code": "ko"},
    ]