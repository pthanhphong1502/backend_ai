# Live Transcription + OCR Server

## Yêu cầu
- Python 3.9+
- pip

## Cài đặt
```bash
pip install -r requirements.txt
```

## Tải model Vosk
Tải model Vosk (ví dụ English) từ https://alphacephei.com/vosk/models và giải nén vào thư mục `model/`.

Ví dụ:
```bash
mkdir model
cd model
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15/* .
```

## Chạy server
```bash
export GOOGLE_API_KEY="your_api_key_here"
python server.py
```

- WebSocket server: ws://localhost:5000 (Live Transcription)
- HTTP API: http://localhost:8000/ocr (OCR Gemini)

## Test OCR API
```bash
curl -X POST -F "file=@sample.png" http://localhost:8000/ocr
```

## Android App
- WebSocket: connect tới ws://<server-ip>:5000 để gửi audio PCM
- OCR: gửi file bằng HTTP POST tới http://<server-ip>:8000/ocr
