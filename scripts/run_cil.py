import sys
from app.stt import STT
from app.tts import TTSWrapper
from app.agent_april import AprilAgent
from app.profiler import maybe_store

stt   = STT()
tts   = TTSWrapper()
agent = AprilAgent()

print("🎤 5 초간 녹음 후 대화합니다. (Ctrl‑C 종료)")
while True:
    audio = stt.record(seconds=5)
    text  = stt.transcribe(audio)
    if not text: continue
    print("👤:", text)
    maybe_store(text)
    reply = agent.chat(text)
    print("🤖:", reply)
    tts.speak(reply)