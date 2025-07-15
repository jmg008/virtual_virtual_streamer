from fastapi import FastAPI, WebSocket
from .agent_april import AprilAgent
from .stt import STT
from .tts import TTSWrapper
from .profiler import maybe_store

app = FastAPI(title="April VTuber API")
agent = AprilAgent()
stt   = STT()
tts   = TTSWrapper()

@app.websocket("/ws/chat")
async def ws_chat(ws: WebSocket):
    await ws.accept()
    while True:
        msg = await ws.receive_text()
        maybe_store(msg)                # 로그를 메모리 후보로
        reply = agent.chat(msg)
        await ws.send_text(reply)
        tts.speak(reply)                # 음성 반환