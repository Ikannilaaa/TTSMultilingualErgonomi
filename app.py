# app.py
import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from tts_service_edge_prosody import process_tts, AUDIO_OUTPUT_DIR
# from tts_service_elevenlabs import process_tts, AUDIO_OUTPUT_DIR
# from tts_service_gemini import process_tts, AUDIO_OUTPUT_DIR
# from tts_service import process_tts, AUDIO_OUTPUT_DIR
# from tts_service_edge import process_tts, AUDIO_OUTPUT_DIR

app = Flask(__name__)

# Teks dummy analisis (Default Bahasa Indonesia)
DUMMY_ANALYSIS_TEXT = """Posisi kerja berbahaya. Posisi kerja perlu diperbaiki dengan memastikan tinggi meja sejajar dengan siku agar lengan dapat berada pada posisi netral. Pastikan pergelangan tangan sejajar dengan lengan bawah. Hindari posisi kerja membungkuk dengan menyesuaikan jarak meja kerja serta dapat menggunakan bantuan kursi kerja ergonomis atau meja dengan fitur adjustable high"""

@app.route("/")
def index():
    return render_template("tts_dummy.html")

@app.route("/images/<path:filename>")
def serve_image(filename):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(root_dir, filename)

@app.route("/audio/<path:filename>")
def audio(filename):
    return send_from_directory(AUDIO_OUTPUT_DIR, filename)

@app.route("/api/analyze-pose", methods=["POST"])
def api_analyze_pose():
    print("Menerima request analisis...")
    
    # Target_lang dari request form (Default 'id')
    target_lang = request.form.get('lang', 'id')
    print(f"Target Bahasa: {target_lang}")
    
    # Terjemahkan teks analisis dummy ke bahasa target
    tts_result = process_tts(DUMMY_ANALYSIS_TEXT, target_lang=target_lang)

    if "error" in tts_result:
        return jsonify(tts_result), 500

    # Siapkan response
    response_data = {
        "status": "success",
        "analysis_text": tts_result['translated_text'], 
        "audio_filename": tts_result['audio_filename']
    }
    
    return jsonify(response_data), 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
