#!/usr/bin/env python3
"""
April VTuber AI 메인 실행 파일
"""

import asyncio
import sys
from app import AprilAgent, STT
from app.profiler import record_conversation, maybe_store
from app.live_chat import LiveChatManager

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
                print(f"April: {response}")
                
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
                
                # AI 응답 생성 (TTS 포함)
                response = await self.agent.respond(user_input, use_tts=True)
                print(f"April: {response}")
                
                # 대화 기록
                record_conversation(user_input, response)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"오류 발생: {e}")
    
    async def live_chat_mode(self, video_id: str, interval: int = 10):
        """라이브 채팅 모드"""
        print(f"🔴 라이브 채팅 모드 시작")
        print(f"비디오 ID: {video_id}")
        print(f"응답 간격: {interval}초")
        print("Ctrl+C로 중단할 수 있습니다.\n")
        
        chat_manager = LiveChatManager(video_id=video_id, interval=interval)
        try:
            await chat_manager.start_monitoring()
        except KeyboardInterrupt:
            print("\n라이브 채팅 모드를 중단합니다.")
        finally:
            await chat_manager.stop_monitoring()

async def main():
    """메인 함수"""
    april = AprilMain()
    
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python main.py voice          # 음성 대화 모드")
        print("  python main.py text           # 텍스트 채팅 모드") 
        print("  python main.py live <비디오ID> [간격]  # 라이브 채팅 모드")
        print("\n예시:")
        print("  python main.py live dQw4w9WgXcQ 10")
        return
    
    mode = sys.argv[1].lower()
    
    if mode == "voice":
        april.running = True
        await april.voice_interaction_loop()
        
    elif mode == "text":
        april.running = True
        await april.text_interaction_loop()
        
    elif mode == "live":
        if len(sys.argv) < 3:
            print("라이브 모드는 비디오 ID가 필요합니다.")
            print("예시: python main.py live dQw4w9WgXcQ")
            return
            
        video_id = sys.argv[2]
        interval = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        
        await april.live_chat_mode(video_id, interval)
        
    else:
        print(f"알 수 없는 모드: {mode}")
        print("사용 가능한 모드: voice, text, live")
    
    print("April AI를 종료합니다.")

if __name__ == "__main__":
    asyncio.run(main())
