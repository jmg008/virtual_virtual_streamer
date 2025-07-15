from typing import Optional
import google.generativeai as gen_ai
import json
import os
from datetime import datetime
from .core_memory import CoreMemory, Slot
from .config import get_settings

settings = get_settings()
gen_ai.configure(api_key=settings.gemini_api_key)
model = gen_ai.GenerativeModel(settings.model_profiler)
core = CoreMemory()

PROMPT = """\
You are Profiler. Decide whether the following user line should become lasting memory.
Record the memory only if it is important and relevant to the user's identity, preferences, or values.
Line: {line}

Respond ONLY in JSON format:
{{
  "slot": "<one of {slots} or null>",
  "entry": "<concise memory or empty>",
  "reason": "<why>"
}}
""".replace("{slots}", ", ".join(Slot.__args__))

def maybe_store(line: str) -> Optional[dict]:
    """사용자 입력을 분석하여 메모리에 저장할지 결정"""
    try:
        print(f"Processing line: {line}")
        
        # Gemini AI를 사용하여 메모리 저장 여부 판단
        response = model.generate_content(PROMPT.format(line=line))
        response_text = response.text.strip()
        
        # 응답이 비어있는지 확인
        if not response_text:
            print("Empty response from AI")
            return None
            
        print(f"AI response: {response_text}")
        
        # 마크다운 코드 블록에서 JSON 추출
        if "```json" in response_text:
            # ```json과 ``` 사이의 내용 추출
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            if end != -1:
                response_text = response_text[start:end].strip()
            else:
                response_text = response_text[start:].strip()
        elif "```" in response_text:
            # 일반 코드 블록에서 추출
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            if end != -1:
                response_text = response_text[start:end].strip()
            else:
                response_text = response_text[start:].strip()
        
        # JSON 파싱 시도
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as json_error:
            print(f"JSON parsing error: {json_error}")
            print(f"Cleaned response: {response_text}")
            return None
        
        # slot이 null이 아니고 entry가 있으면 메모리에 저장
        if result.get("slot") and result.get("entry") and result.get("reason"):
            slot = result["slot"]
            entry = result["entry"]
            reason = result["reason"]
            # CoreMemory의 실제 메서드 사용 (store 대신 add 또는 append)
            try:
                core.upsert(slot, entry, reason)
            except Exception as store_error:
                print(f"Error storing memory: {store_error}")
                return None
            
            print(f"Stored in {slot}: {entry}")
            return result
        else:
            print(f"Not storing: {result.get('reason', 'No reason provided')}")
            return None
            
    except Exception as e:
        print(f"Error in maybe_store: {e}")
        return None

def record_conversation(user_input: str, ai_response: str) -> None:
    """대화 내용을 로그 파일에 기록"""
    log_dir = "data/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "user": user_input,
        "ai": ai_response
    }
    
    # 오늘 날짜로 로그 파일 생성
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"conversation_{today}.json")
    
    # 기존 로그 읽기 또는 새 리스트 생성
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    else:
        logs = []
    
    # 새 로그 추가
    logs.append(log_entry)
    
    # 로그 파일에 저장
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)