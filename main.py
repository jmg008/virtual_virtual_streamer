#!/usr/bin/env python3
"""
April VTuber AI 메인 실행 파일
"""

import asyncio
from app import AprilAgent, STT
from app.profiler import record_conversation, maybe_store

class AprilMain:
    def __init__(self):
        self.agent = AprilAgent(enable_tts=True)  # TTS 활성화
        self.stt = STT()
        self.running = False
    
    async def voice_interaction_loop(self):
        """음성 대화 루프"""
        print("April AI가 시작되었습니다. 말씀해 주세요...")
        
        while self.running:
            try:
                # 음성 녹음
                print("🎤 녹음 중... (5초)")
                audio = self.stt.record(seconds=5)
                
                # 음성을 텍스트로 변환
                user_text = self.stt.transcribe(audio)
                if not user_text.strip():
                    continue
                
                print(f"사용자: {user_text}")
                
                # 메모리에 저장할지 판단
                maybe_store(user_text)
                
                # AI 응답 생성 (TTS 포함)
                response = await self.agent.respond(user_text, use_tts=True)
                # print(f"April: {response}")
                
                # 대화 기록
                record_conversation(user_text, response)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"오류 발생: {e}")
    
    async def text_interaction_loop(self):
        """텍스트 대화 루프"""
        print("April AI 텍스트 모드가 시작되었습니다.")
        print("종료하려면 'quit' 또는 'exit'를 입력하세요.")
        
        while self.running:
            try:
                user_input = input("\n사용자: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '종료']:
                    break
                
                if not user_input:
                    continue
                
                # 메모리에 저장할지 판단
                maybe_store(user_input)
                
                # AI 응답 생성
                response = await self.agent.respond(user_input)
                print(f"April: {response}")
                
                # 대화 기록
                record_conversation(user_input, response)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"오류 발생: {e}")
    
    async def start(self, mode: str = "text"):
        """April AI 시작"""
        self.running = True
        
        if mode == "voice":
            await self.voice_interaction_loop()
        else:
            await self.text_interaction_loop()
        
        print("April AI를 종료합니다.")

async def main():
    """메인 함수"""
    import sys
    
    mode = "text"
    if len(sys.argv) > 1 and sys.argv[1] == "--voice":
        mode = "voice"
    
    april = AprilMain()
    await april.start(mode)

if __name__ == "__main__":
    asyncio.run(main())