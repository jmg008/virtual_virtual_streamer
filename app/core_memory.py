# app/core_memory.py
"""
코어 메모리 – JSON 파일 버전
---------------------------------
* 저장 위치: data/core_memory.json
* 쓰기 권한: Profiler 전용
* 읽기 권한: April(Agent) · Profiler
"""

from __future__ import annotations
import json, hashlib, threading
from pathlib import Path
from datetime import datetime
from typing import Literal, Dict, List, Any

from .config import DATA_DIR

JSON_PATH = DATA_DIR / "core_memory.json"
_LOCK     = threading.Lock()           # 파일 동시 접근 보호

Slot = Literal[
    "identity", "preferences", "ethics",
    "values", "ideology", "boundaries"
]

# ───────────────────────────────────────────────────────────
# 내부 헬퍼
# ───────────────────────────────────────────────────────────
def _empty_memory() -> Dict[str, List[Dict[str, Any]]]:
    """6 슬롯을 모두 갖는 초기 구조 반환"""
    return {s: [] for s in Slot.__args__}

def _load() -> Dict[str, List[Dict[str, Any]]]:
    if not JSON_PATH.exists():
        JSON_PATH.write_text(json.dumps(_empty_memory(), ensure_ascii=False, indent=2))
    with JSON_PATH.open("r", encoding="utf‑8") as f:
        return json.load(f)

def _dump(data: Dict[str, Any]) -> None:
    with JSON_PATH.open("w", encoding="utf‑8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ───────────────────────────────────────────────────────────
# 공개 클래스
# ───────────────────────────────────────────────────────────
class CoreMemory:
    """파일 기반 코어 메모리 관리자"""

    def __init__(self) -> None:
        # 최초 호출 시 파일 생성 보증
        if not JSON_PATH.exists():
            JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
            _dump(_empty_memory())

    # ---------- 쓰기 ----------
    def upsert(self, slot: Slot, entry: str, reason: str) -> None:
        """
        (slot, entry) 조합이 없으면 새로 저장.
        동일 entry 는 해시 중복으로 필터링한다.
        """
        with _LOCK:
            data = _load()
            bucket: List[Dict[str, Any]] = data[slot]

            key = hashlib.sha256(entry.encode()).hexdigest()
            if any(row["id"] == key for row in bucket):
                return  # 이미 존재 → no-op

            bucket.append({
                "id":      key,
                "entry":   entry,
                "reason":  reason,
                "created": datetime.utcnow().isoformat(timespec="seconds") + "Z"
            })
            _dump(data)

    # ---------- 읽기 ----------
    def export_json(self) -> str:
        """
        에이전트 프롬프트 용도로
        {slot: [entry, …]} 형태의 경량 JSON 문자열 반환
        """
        with _LOCK:
            try:
                raw = _load()
                result = {slot: [row["entry"] for row in bucket] for slot, bucket in raw.items()}
                return json.dumps(result, ensure_ascii=False)
            except Exception:
                # 오류 발생 시 빈 JSON 객체 반환
                return "{}"
