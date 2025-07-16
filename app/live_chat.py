# app/live_chat.py
"""
유튜브 라이브 채팅 수집 및 응답 시스템
"""

import asyncio
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

try:
    import pytchat
except ImportError:
    pytchat = None
    print("경고: pytchat 라이브러리가 설치되지 않았습니다. 'pip install pytchat' 실행하세요.")

from .agent_april import AprilAgent
from .profiler import record_conversation, maybe_store

@dataclass
class ChatMessage:
    """채팅 메시지 데이터 클래스"""
    author: str
    message: str
    timestamp: datetime
    
class LiveChatManager:
    """라이브 채팅 관리자"""
    
    def __init__(self, video_id: str = None, interval: int = 10):
        """
        Args:
            video_id: 유튜브 라이브 스트림 비디오 ID
            interval: 댓글 수집 및 응답 간격 (초)
        """
        self.video_id = video_id
        self.interval = interval
        self.april_agent = AprilAgent(enable_tts=True)
        self.chat_buffer: List[ChatMessage] = []
        self.is_running = False
        self.chat_session = None
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def set_video_id(self, video_id: str):
        """비디오 ID 설정"""
        self.video_id = video_id
        self.logger.info(f"비디오 ID 설정됨: {video_id}")
        
    def _collect_recent_messages(self) -> List[ChatMessage]:
        """최근 메시지들 수집"""
        if not pytchat or not self.chat_session:
            return []
            
        messages = []
        try:
            # pytchat에서 새로운 메시지들 가져오기
            data = self.chat_session.get()
            current_time = datetime.now()
            
            for item in data.items:
                message = ChatMessage(
                    author=item.author.name,
                    message=item.message,
                    timestamp=current_time
                )
                messages.append(message)
                
        except Exception as e:
            self.logger.error(f"메시지 수집 오류: {e}")
            
        return messages
    
    def _aggregate_messages(self, messages: List[ChatMessage]) -> str:
        """메시지들을 집계하여 하나의 입력으로 만들기"""
        if not messages:
            return ""
            
        # 메시지 개수와 주요 내용 요약
        message_count = len(messages)
        unique_authors = len(set(msg.author for msg in messages))
        
        # 메시지 내용들
        chat_content = []
        for msg in messages[-10:]:  # 최근 10개만 선택
            chat_content.append(f"{msg.author}: {msg.message}")

# 시청자들이 {self.interval}초 동안 {message_count}개의 댓글을 남겼습니다. 
# {unique_authors}명의 서로 다른 시청자들이 참여했습니다.
     
        # 집계된 프롬프트 생성
        aggregated_prompt = f"""
당신의 실시간 스트리밍에 시청자들이 남긴 댓글입니다.

최근 댓글들:
{chr(10).join(chat_content)}

위 댓글들을 바탕으로 시청자들과 자연스럽게 대화하세요. 
개별 댓글에 일일이 답하지 말고, 전체적인 분위기나 주요 화제를 파악해서 응답해주세요.
"""
        return aggregated_prompt.strip()
    
    def _should_respond(self, messages: List[ChatMessage]) -> bool:
        """응답할지 여부 결정"""
        if not messages:
            return False
            
        # 최소 3개 이상의 메시지가 있을 때만 응답
        if len(messages) < 3:
            return False
            
        # 스팸이나 반복 메시지 필터링
        unique_messages = set(msg.message.strip().lower() for msg in messages)
        if len(unique_messages) < len(messages) * 0.7:  # 70% 이상이 유니크해야 함
            return False
            
        return True
    
    async def _process_chat_batch(self):
        """채팅 배치 처리"""
        try:
            # 최근 메시지 수집
            new_messages = self._collect_recent_messages()
            
            if not new_messages:
                self.logger.debug("새로운 메시지가 없습니다.")
                return
                
            self.chat_buffer.extend(new_messages)
            self.logger.info(f"{len(new_messages)}개의 새 메시지 수집됨")
            
            # 응답할지 결정
            if not self._should_respond(new_messages):
                self.logger.debug("응답 조건에 맞지 않음")
                return
                
            # 메시지 집계
            aggregated_input = self._aggregate_messages(new_messages)
            
            if not aggregated_input:
                return
                
            self.logger.info("에이프릴 응답 생성 중...")
            
            # 프로파일러에 저장 (선택적)
            sample_messages = [msg.message for msg in new_messages[:3]]
            maybe_store(" | ".join(sample_messages))
            
            # 에이프릴 응답 생성 (TTS 포함)
            response = await self.april_agent.respond(aggregated_input, use_tts=True)
            
            self.logger.info(f"에이프릴 응답: {response}")
            
            # 대화 기록
            record_conversation(aggregated_input, response)
            
            # 처리된 메시지들 제거 (메모리 관리)
            self.chat_buffer = self.chat_buffer[-50:]  # 최근 50개만 유지
            
        except Exception as e:
            self.logger.error(f"채팅 배치 처리 오류: {e}")
    
    async def start_monitoring(self):
        """라이브 채팅 모니터링 시작"""
        if not pytchat:
            self.logger.error("pytchat 라이브러리가 필요합니다.")
            return
            
        if not self.video_id:
            self.logger.error("비디오 ID가 설정되지 않았습니다.")
            return
            
        try:
            # pytchat 세션 시작
            self.chat_session = pytchat.create(video_id=self.video_id)
            self.is_running = True
            
            self.logger.info(f"라이브 채팅 모니터링 시작 (비디오 ID: {self.video_id})")
            self.logger.info(f"응답 간격: {self.interval}초")
            
            while self.is_running and self.chat_session.is_alive():
                try:
                    await self._process_chat_batch()
                    await asyncio.sleep(self.interval)
                    
                except KeyboardInterrupt:
                    self.logger.info("사용자에 의해 중단됨")
                    break
                except Exception as e:
                    self.logger.error(f"모니터링 루프 오류: {e}")
                    await asyncio.sleep(self.interval)
                    
        except Exception as e:
            self.logger.error(f"채팅 세션 시작 오류: {e}")
        finally:
            await self.stop_monitoring()
    
    async def stop_monitoring(self):
        """라이브 채팅 모니터링 중단"""
        self.is_running = False
        if self.chat_session:
            try:
                self.chat_session.terminate()
            except Exception as e:
                self.logger.error(f"채팅 세션 종료 오류: {e}")
        
        self.logger.info("라이브 채팅 모니터링 중단됨")
    
    def get_stats(self) -> Dict:
        """통계 정보 반환"""
        return {
            "is_running": self.is_running,
            "video_id": self.video_id,
            "interval": self.interval,
            "buffer_size": len(self.chat_buffer),
            "chat_alive": self.chat_session.is_alive() if self.chat_session else False
        }


# 간편 사용을 위한 함수
async def start_live_chat_bot(video_id: str, interval: int = 10):
    """라이브 채팅 봇 시작"""
    manager = LiveChatManager(video_id=video_id, interval=interval)
    await manager.start_monitoring()
    return manager
