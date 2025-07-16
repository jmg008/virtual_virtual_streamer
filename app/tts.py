from google import genai
from google.genai import types
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
import re
import threading
import time
import subprocess
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
        
        # 감정별 키 매핑
        self.emotion_keys = {
            'laugh': '1',    # 웃음 - Alt+1
            'angry': '2',    # 화남 - Alt+2  
            'sad': '3',      # 슬픔 - Alt+3
            'smile': '4',    # 미소 - Alt+4
            'surprise': '5'  # 놀람 - Alt+5
        }
        
        # 감정 키워드 패턴
        self.emotion_patterns = {
            'laugh': [
                r'하하+', r'호호+', r'히히+', r'크크+', r'ㅋ+', r'ㅎ+',
                r'웃', r'재미있', r'우스운', r'코믹', r'폭소', r'미소',
                r'기쁘', r'즐거운', r'신나', r'유쾌한'
            ],
            'angry': [
                r'화나', r'짜증', r'분노', r'열받', r'빡쳐', r'어이없',
                r'답답', r'귀찮', r'불쾌', r'불만', r'억울', r'기분나쁜'
            ],
            'sad': [
                r'슬프', r'우울', r'눈물', r'울', r'서글픈', r'비참',
                r'처량', r'암울', r'절망', r'힘들', r'괴롭', r'아프'
            ],
            'smile': [
                r'좋', r'행복', r'만족', r'고마', r'감사', r'따뜻',
                r'평화', r'편안', r'달콤', r'상냥', r'친근', r'온화'
            ],
            'surprise': [
                r'놀라', r'깜짝', r'어?', r'헉', r'앗', r'우와',
                r'대박', r'신기', r'이상', r'예상외', r'뜻밖', r'의외'
            ]
        }
    
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
            # 텍스트에서 감정 감지
            detected_emotion = self._detect_emotion(text)
            
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
                
                # 감정 표현 처리 (음성 재생 전에 실행)
                if detected_emotion:
                    self._handle_emotion_expression(detected_emotion)
                
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
            
    def test_emotion_detection(self, text: str):
        """감정 감지 테스트 메서드"""
        print(f"테스트 텍스트: {text}")
        emotion = self._detect_emotion(text)
        if emotion:
            print(f"감지된 감정: {emotion}")
            self._handle_emotion_expression(emotion)
        else:
            print("감정이 감지되지 않았습니다.")
    
    def set_voice(self, voice_name: str):
        """음성 변경"""
        self.voice_id = voice_name
    
    def _detect_emotion(self, text: str) -> str:
        """텍스트에서 감정을 감지"""
        text = text.lower()
        
        # 각 감정별 키워드 매칭 스코어 계산
        emotion_scores = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text))
                score += matches
            emotion_scores[emotion] = score
        
        # 가장 높은 스코어의 감정 반환
        if any(score > 0 for score in emotion_scores.values()):
            detected_emotion = max(emotion_scores, key=emotion_scores.get)
            print(f"감정 감지: {detected_emotion} (텍스트: {text[:50]}...)")
            return detected_emotion
        
        return None
    
    def _send_keyboard_input(self, key: str):
        """macOS에서 Alt+키 조합 전송"""
        try:
            # osascript를 사용하여 키보드 입력 전송
            script = f'''
            tell application "System Events"
                key code {self._get_key_code(key)} using option down
            end tell
            '''
            subprocess.run(['osascript', '-e', script], check=True)
            print(f"키보드 입력 전송: Alt+{key}")
        except Exception as e:
            print(f"키보드 입력 오류: {e}")
    
    def _get_key_code(self, key: str) -> str:
        """숫자 키의 키코드 반환 (macOS)"""
        key_codes = {
            '1': '18',  # Alt+1
            '2': '19',  # Alt+2
            '3': '20',  # Alt+3
            '4': '21',  # Alt+4
            '5': '23'   # Alt+5
        }
        return key_codes.get(key, '18')
    
    def _handle_emotion_expression(self, emotion: str):
        """감정 표현 처리 (키 입력 및 타이머)"""
        if emotion and emotion in self.emotion_keys:
            key = self.emotion_keys[emotion]
            
            # 즉시 키 입력
            self._send_keyboard_input(key)
            
            # 3초 후 같은 키를 다시 눌러서 표정 해제
            def reset_expression():
                time.sleep(3)
                self._send_keyboard_input(key)
                print(f"표정 해제: Alt+{key}")
            
            # 별도 스레드에서 타이머 실행
            timer_thread = threading.Thread(target=reset_expression, daemon=True)
            timer_thread.start()