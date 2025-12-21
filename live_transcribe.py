import asyncio
import websockets
import json
import subprocess          # thêm
from vosk import Model, KaldiRecognizer

SAMPLE_RATE = 16000
model = Model("model")

# ================== WEBSOCKET LIVE TRANSCRIBE ==================

async def handle_client(ws, path):
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    print("Client connected")
    try:
        async for message in ws:
            if isinstance(message, bytes):
                if rec.AcceptWaveform(message):
                    res = json.loads(rec.Result())
                    await ws.send(json.dumps({"type": "final", "text": res.get("text", "")}))
                else:
                    partial = json.loads(rec.PartialResult())
                    await ws.send(json.dumps({"type": "partial", "text": partial.get("partial", "")}))
            else:
                print("Text message:", message)
    except websockets.ConnectionClosed:
        print("Client disconnected")

async def start_ws_server():
    async with websockets.serve(handle_client, "0.0.0.0", 5000):
        print("WS Server: ws://0.0.0.0:5000")
        await asyncio.Future()

# ================== TRANSCRIBE FILE MP3/WAV ==================

def transcribe_audio_file(path: str) -> str:
    """
    Nhận đường dẫn file audio (mp3, wav, m4a,...)
    Dùng ffmpeg + Vosk để chuyển sang text, trả về 1 chuỗi.
    """

    # Yêu cầu: máy phải cài ffmpeg và có trong PATH
    process = subprocess.Popen(
        [
            "ffmpeg",
            "-loglevel", "quiet",
            "-i", path,
            "-ar", str(SAMPLE_RATE),
            "-ac", "1",
            "-f", "s16le",
            "-"
        ],
        stdout=subprocess.PIPE
    )

    rec = KaldiRecognizer(model, SAMPLE_RATE)
    full_text = []

    while True:
        data = process.stdout.read(4000)
        if len(data) == 0:
            break

        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            text = res.get("text", "")
            if text:
                full_text.append(text)

    # lấy kết quả cuối cùng
    final_res = json.loads(rec.FinalResult())
    final_text = final_res.get("text", "")
    if final_text:
        full_text.append(final_text)

    return " ".join(full_text).strip()
