from google import genai
from google.genai import types
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
from .config import get_settings

settings = get_settings()

class TTSWrapper:
    def __init__(self, voice_id: str = "Leda"):
        """
        TTS 래퍼 클래스
        voice_id: 사용할 음성 (기본값: Kore - 회사 톤)
        """
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.voice_id = voice_id
    
    def _wave_file(self, filename: str, pcm_data: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2):
        """WAV 파일 생성 (Gemini 공식 문서 방식)"""
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm_data)
    
    def _load_wav_file(self, filename: str) -> np.ndarray:
        """WAV 파일을 numpy 배열로 로드"""
        try:
            with wave.open(filename, 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                audio = np.frombuffer(frames, dtype=np.int16)
                return audio.astype(np.float32) / 32767.0
        except Exception as e:
            print(f"WAV 파일 로드 오류: {e}")
            return np.array([])

    def speak(self, text: str):
        """텍스트를 음성으로 변환하고 재생"""
        try:
            # Gemini 2.5 TTS 모델로 음성 생성
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=self.voice_id,
                            )
                        )
                    ),
                )
            )
            
            # 오디오 데이터 추출
            audio_data = response.candidates[0].content.parts[0].inline_data.data
            
            # 임시 WAV 파일 생성
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_filename = tmp_file.name
            
            try:
                # 공식 문서 방식으로 WAV 파일 생성
                self._wave_file(tmp_filename, audio_data)
                
                # WAV 파일을 numpy 배열로 로드하고 재생
                audio_array = self._load_wav_file(tmp_filename)
                if len(audio_array) > 0:
                    sd.play(audio_array, samplerate=24000)
                    sd.wait()  # 재생 완료까지 대기
                else:
                    print(f"오디오 배열이 비어있음: {text}")
                    
            except Exception as audio_error:
                print(f"오디오 처리 오류: {audio_error}")
                print(f"텍스트: {text}")
            finally:
                # 임시 파일 삭제
                if os.path.exists(tmp_filename):
                    os.unlink(tmp_filename)
                    
        except Exception as e:
            print(f"TTS API 오류: {e}")
            print(f"음성 변환 실패 - 텍스트: {text}")
            
    def set_voice(self, voice_name: str):
        """음성 변경"""
        self.voice_id = voice_name