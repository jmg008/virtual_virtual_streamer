#!/bin/bash
# install_dependencies.sh
# 라이브 채팅 기능을 위한 필수 패키지 설치

echo "April AI 라이브 채팅 기능을 위한 패키지를 설치합니다..."

# pytchat 설치
echo "pytchat 설치 중..."
pip install pytchat

# 기타 필요한 패키지들
echo "기타 패키지 설치 중..."
pip install asyncio-throttle

echo "설치 완료!"
echo ""
echo "사용법:"
echo "  python main.py live <유튜브_비디오_ID> [응답간격초]"
echo ""
echo "예시:"
echo "  python main.py live dQw4w9WgXcQ 10"
