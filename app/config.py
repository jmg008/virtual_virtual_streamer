from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR  = DATA_DIR / "logs"
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

class Settings(BaseSettings):
    gemini_api_key: str = Field(default="AIzaSyDIiTATl_hYzT1_71baEqQHCzulGIAK_wg", env="GEMINI_API_KEY")
    model_april:    str = "gemini-2.0-flash"
    model_profiler: str = "gemini-2.0-flash"
    stt_model:      str = "large-v3"
    voice_id:       str = "random"
    
    class Config:
        env_file = BASE_DIR / ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()          # singleton