# gemini.py에 통합됨
# 사유: 제미나이 클라이언트 두번 불러오면 시간 오래걸림

from google import genai
from google.genai import types
import re

client = genai.Client(api_key = "AIzaSyDIiTATl_hYzT1_71baEqQHCzulGIAK_wg")
profiler_prompt = open("profiler_prompt.txt", "r", encoding="utf-8").read()

def profiling(log):
    response = client.models.generate_content(
        model = "gemini-2.5-pro",
        config = types.GenerateContentConfig(
            system_instruction = f"# 기존 코어 메모리\n{open("april_core_memory.json", "r", encoding="utf-8").read()}\n\n# 프롬프트\n{profiler_prompt}"
        ),
        contents = log
    )

    mem_file = open("april_core_memory.json", 'w', encoding='utf-8')
    memory = re.search("```json(.*)```", response.text, re.S)[1].strip()
    mem_file.write(memory)