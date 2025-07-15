import numpy as np
import sounddevice as sd
import io
import wave
from google.genai import types
import google.generativeai as genai
from .config import get_settings

settings = get_settings()

class STT:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.client = genai.GenerativeModel('gemini-2.0-flash-exp')

    def record(self, seconds: int = 5, fs: int = 16_000) -> np.ndarray:
        audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        sd.wait()
        return audio.flatten().astype(np.float32)

    def _audio_to_bytes(self, audio: np.ndarray, fs: int = 16_000) -> bytes:
        # Convert numpy array to WAV bytes
        audio_int16 = (audio * 32767).astype(np.int16)
        
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(fs)
            wav_file.writeframes(audio_int16.tobytes())
        
        return buffer.getvalue()

    def transcribe(self, audio: np.ndarray) -> str:
        audio_bytes = self._audio_to_bytes(audio)
        
        response = self.client.generate_content([
            'Please transcribe this audio clip and return only the transcribed text without any additional commentary.',
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type='audio/wav',
            )
        ])
        
        return response.text.strip()