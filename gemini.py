from google import genai
from google.genai import types
import re

client = genai.Client(api_key = "AIzaSyDIiTATl_hYzT1_71baEqQHCzulGIAK_wg")
april_base_prompt = open("april_base_prompt.txt", "r", encoding="utf-8").read()
profiler_prompt = open("profiler_prompt.txt", "r", encoding="utf-8").read()

def chat(user_input, log):
    april_core_mem = open("april_core_memory.json", "r", encoding="utf-8").read()
    april_response = client.models.generate_content(
        model = "gemini-2.5-flash",
        config = types.GenerateContentConfig(
            system_instruction = f"# 채팅 로그\n{log}\n\n# 코어 메모리\n{april_core_mem}\n\n# 기초 프롬프트\n{april_base_prompt}"
        ),
        contents = user_input
        )
    return april_response.text

def profiling(log):
    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        config = types.GenerateContentConfig(
            system_instruction = f"# 기존 코어 메모리\n{open("april_core_memory.json", "r", encoding="utf-8").read()}\n\n# 프롬프트\n{profiler_prompt}"
        ),
        contents = log
    )

    mem_file = open("april_core_memory.json", 'w', encoding='utf-8')
    memory = re.search("```json(.*)```", response.text, re.S)[1].strip()
    mem_file.write(memory)

def stting(audio):
    response = client.models.generate_content(
        model = "gemini-2.5-flash-lite-preview-06-17",
        config = types.GenerateContentConfig(
            system_instruction = open("stt_prompt.txt", 'r', encoding='utf-8').read()
        ),
        contents = types.Part.from_bytes(
            data=audio,
            mime_type="audio/wav"
        )
    )
    return response.text