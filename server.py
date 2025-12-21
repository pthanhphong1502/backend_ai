import asyncio
from multiprocessing import Process
from live_transcribe import start_ws_server
from ocr_api import app

def run_ws():
    asyncio.run(start_ws_server())

def run_http():
    app.run(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    p1 = Process(target=run_ws)
    p2 = Process(target=run_http)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
