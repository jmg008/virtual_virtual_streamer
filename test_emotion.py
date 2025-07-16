#!/usr/bin/env python3
"""
에이프릴 감정 표현 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.tts import TTSWrapper

def test_emotion_expressions():
    """감정 표현 테스트"""
    tts = TTSWrapper()
    
    # 테스트할 감정별 텍스트
    test_cases = [
        ("웃음", "하하하 정말 재미있는 이야기네요! 너무 웃겨요 ㅋㅋㅋ"),
        ("화남", "정말 화가 나네요! 이건 너무 짜증나는 일이에요"),
        ("슬픔", "너무 슬퍼요... 눈물이 날 것 같아요"),
        ("미소", "정말 좋네요! 행복한 기분이에요. 감사합니다"),
        ("놀람", "어? 정말 놀라운데요! 깜짝 놀랐어요. 대박!")
    ]
    
    print("에이프릴 감정 표현 테스트를 시작합니다.")
    print("각 테스트 후 3초간 표정이 유지되고 자동으로 해제됩니다.\n")
    
    for emotion_name, text in test_cases:
        print(f"\n=== {emotion_name} 테스트 ===")
        print(f"텍스트: {text}")
        
        # 감정 감지만 테스트 (실제 TTS는 실행하지 않음)
        tts.test_emotion_detection(text)
        
        input("다음 테스트를 진행하려면 Enter를 누르세요...")

if __name__ == "__main__":
    test_emotion_expressions()
