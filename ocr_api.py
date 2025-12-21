from difflib import SequenceMatcher
import os
import tempfile
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from live_transcribe import transcribe_audio_file

load_dotenv()
API_KEYS = os.getenv("GEMINI_API_KEY")

if not API_KEYS:
    raise RuntimeError("No GEMINI_API_KEY* found in .env")

app = Flask(__name__)

OCR_PROMPT = """
You are an OCR engine.
Read all the text in this document.

Return only the exact text you see as a single plain string.
Do not add any explanation, labels, markdown, or summary.
"""

def generate_with_fallback(path: str):
    try:
        # Cấu hình với 1 key duy nhất
        genai.configure(api_key=API_KEYS)
        
        # Khởi tạo model
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

        # Upload file và gọi API
        uploaded = genai.upload_file(path)
        response = model.generate_content([OCR_PROMPT, uploaded])
        
        return response

    except Exception as e:
        # Vì chỉ có 1 key, nếu lỗi thì ném lỗi ra luôn để server biết mà xử lý
        print(f"Error generating content: {e}")
        raise e

@app.route("/ocr", methods=["POST"])
def ocr_endpoint():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    tmp_dir = tempfile.gettempdir()
    path = os.path.join(tmp_dir, file.filename)
    file.save(path)

    try:
        response = generate_with_fallback(path)
        return jsonify({"text": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# 2) CHECK PHÁT ÂM TỪ FILE AUDIO
@app.route("/check_pronunciation", methods=["POST"])
def check_pronunciation():
    """
    Request:
      - file: audio (mp3, wav, m4a...)
      - target: text chuẩn muốn người dùng đọc

    Response:
      - target: câu chuẩn
      - recognized: câu Vosk nhận ra
      - score: độ giống 0-1
      - is_correct: True/False theo ngưỡng
    """
    if "file" not in request.files or "target" not in request.form:
        return jsonify({"error": "Missing 'file' or 'target'"}), 400

    file = request.files["file"]
    target = request.form["target"]

    # lưu file tạm
    tmp_dir = tempfile.gettempdir()
    path = os.path.join(tmp_dir, file.filename)
    file.save(path)

    try:
        recognized = transcribe_audio_file(path)

        # chuẩn hóa text để so similarity
        def normalize(s: str) -> str:
            s = s.lower()
            return "".join(ch for ch in s if ch.isalnum() or ch.isspace()).strip()

        norm_target = normalize(target)
        norm_rec = normalize(recognized)

        score = SequenceMatcher(None, norm_target, norm_rec).ratio()
        is_correct = score >= 0.8   # em muốn khó hơn thì tăng lên, dễ hơn thì giảm xuống

        return jsonify({
            "target": target,
            "recognized": recognized,
            "score": score,
            "is_correct": is_correct
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
