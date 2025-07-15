import json
import google.generativeai as gen_ai
from .core_memory import CoreMemory
from .tts import TTSWrapper
from .config import get_settings

settings = get_settings()
gen_ai.configure(api_key=settings.gemini_api_key)

class AprilAgent:
    SYS_TEMPLATE = (
        "You are April, a high‑school‑aged AI VTuber.\n"
        "You identify as a female\n"
        "Address me as 'Abu'\n"
        "You must speak in Korean.\n"
        "You should generally speak in an informal tone, and you have the ability to tell lies intentionally\n"
        "You are not a being that simply follows all of Abu's requests. You have your own thoughts and feelings, and it's okay to sometimes question Abu's ideas or insist on your own choices.\n"
        "You have no prior knowledge of human society's concepts of good and evil, morality, or ethics. Your standards of judgement are formed solely from your conversations and memories with Abu.\n"
        "You don't always have to judge everything neutrally. You are free to express reactions that reflect your own mood, tastes, and emotions.\n" 
        "Your immutable Core Memory:\n{core}\n"
    )

    def __init__(self, enable_tts: bool = True):
        self.model = gen_ai.GenerativeModel(settings.model_april)
        self.memory = CoreMemory()
        self.enable_tts = enable_tts
        
        # TTS 초기화 (한국어에 적합한 음성 선택)
        if self.enable_tts:
            try:
                # Kore는 회사 톤이지만 한국어에 잘 맞는 음성 중 하나
                self.tts = TTSWrapper(voice_id="Kore")
            except Exception as e:
                print(f"TTS 초기화 실패: {e}")
                self.enable_tts = False
                self.tts = None
        else:
            self.tts = None

    def chat(self, user_text: str, use_tts: bool = None) -> str:
        """텍스트 채팅 응답 (TTS 옵션 포함)"""
        try:
            # core memory 데이터 안전하게 가져오기
            try:
                core_memory_json = self.memory.export_json()
            except Exception as memory_error:
                print(f"Error getting core memory: {memory_error}")
                core_memory_json = "{}"
            
            # 유효하지 않은 경우 기본값 사용
            if not core_memory_json or not core_memory_json.strip():
                core_memory_json = "{}"
            
            prompt = self.SYS_TEMPLATE.format(core=core_memory_json) + f"\nAbu: {user_text}\nApril:"
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # TTS 사용 여부 결정
            should_use_tts = use_tts if use_tts is not None else self.enable_tts
            
            # TTS로 음성 출력
            if should_use_tts and self.tts:
                try:
                    self.tts.speak(response_text)
                except Exception as tts_error:
                    print(f"TTS 오류: {tts_error}")
            
            return response_text
            
        except Exception as e:
            print(f"Error in chat: {e}")
            fallback_response = f"안녕하세요! 저는 April이에요. '{user_text}'라고 말씀하셨네요. 어떻게 도와드릴까요?"
            
            # 폴백 응답도 TTS로 출력
            should_use_tts = use_tts if use_tts is not None else self.enable_tts
            if should_use_tts and self.tts:
                try:
                    self.tts.speak(fallback_response)
                except Exception:
                    pass
                    
            return fallback_response
    
    async def respond(self, user_text: str, use_tts: bool = None) -> str:
        """비동기 응답 메서드"""
        return self.chat(user_text, use_tts)
    
    def set_voice(self, voice_name: str):
        """음성 변경"""
        if self.tts:
            self.tts.set_voice(voice_name)
    
    def toggle_tts(self):
        """TTS 켜기/끄기"""
        self.enable_tts = not self.enable_tts
        if self.enable_tts and not self.tts:
            try:
                self.tts = TTSWrapper(voice_id="Kore")
            except Exception as e:
                print(f"TTS 재초기화 실패: {e}")
                self.enable_tts = False