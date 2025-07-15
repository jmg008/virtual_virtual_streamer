"""
April VTuber AI 패키지
---------------------
코어 메모리 기반 VTuber AI 에이전트 시스템
"""

from .core_memory import CoreMemory, Slot
from .profiler import maybe_store
from .stt import STT
from .tts import TTSWrapper
from .config import get_settings, Settings, DATA_DIR, LOG_DIR, BASE_DIR
from .agent_april import AprilAgent

__version__ = "1.0.0"
__author__ = "April Team"

__all__ = [
    # Core components
    "AprilAgent",
    "CoreMemory",
    "Slot",
    
    # Audio processing
    "STT",
    "TTSWrapper",
    
    # Memory management
    "maybe_store",
    
    # Configuration
    "get_settings",
    "Settings",
    "DATA_DIR",
    "LOG_DIR", 
    "BASE_DIR",
]