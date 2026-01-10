# tts_service_gemini.py
import os
import wave
from google import genai
from google.genai import types
from deep_translator import GoogleTranslator

# Ambil API KEY dari environment variable
API_KEY = os.getenv("GENAI_API_KEY")

# Setup Client
client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_OUTPUT_DIR = os.path.join(BASE_DIR, 'output_audio')
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

def save_wave_file(filename, pcm_data, channels=1, rate=24000, sample_width=2):
    """Menyimpan data PCM raw ke file WAV."""
    filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
    
    if isinstance(pcm_data, str):
        pcm_data = pcm_data.encode('latin1') # Fallback jika string
    
    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)

    return filename

def process_tts(text, target_lang='id'):
    global client
    # Cek API Key
    if not client:
        api_key = os.getenv("GENAI_API_KEY")
        if not api_key:
            return {"error": "GENAI_API_KEY belum disetting di environment!"}
        client = genai.Client(api_key=api_key)

    try:
        # Translate
        if not text or not text.strip():
            return {"error": "Text kosong"}
        
        text = text.strip()

        print(f"Menerjemahkan ke {target_lang}...")
        try:
            translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        except Exception as e:
            return {"error": f"Gagal Translate: {str(e)}"}
        
        # Generate Audio via Gemini
        print("Generate Audio via Gemini...")

        style_instruction = "Read aloud in a warm and friendly tone: "
        full_prompt = f"{style_instruction}\n\n{translated_text}"
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp", 
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name='Kore',
                        )
                    )
                )
            )
        )
        
        try:
            part = response.candidates[0].content.parts[0]
            inline = getattr(part, 'inline_data', None)
            if not inline or not inline.data:
                raise ValueError("Tidak ada data audio dalam response Gemini.")
            audio_data = inline.data
        except Exception as e:
            raise RuntimeError(f"Gagal parsing audio dari Gemini: {e}")
        
        # Simpan ke file
        filename = f"tts_{target_lang}_{os.urandom(4).hex()}.wav"
        save_wave_file(filename, audio_data)
        
        return {
            "original_text": text,
            "translated_text": translated_text,
            "audio_filename": filename
        }
        
    except Exception as e:
        print(f"Error TTS: {e}")
        return {"error": str(e)}

def get_supported_languages():
    try:
        lang_map = GoogleTranslator(source="auto", target="en").get_supported_languages(as_dict=True)
        return sorted([{"name": name.title(), "code": code} for name, code in lang_map.items()], key=lambda x: x['name'])
    except Exception:
        # Fallback jika gagal fetch language list
        return [{"name": "Indonesian", "code": "id"}, {"name": "English", "code": "en"}]