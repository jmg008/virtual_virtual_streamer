import gemini
import memory_manager as mem
import emotion
import threading
import tts
import stt

class Profiler(threading.Thread):
    def __init__(self):
        super().__init__()
    
    def run(self):
        gemini.profiling(mem.get_context())

class Emotioner(threading.Thread):
    def __init__(self, text):
        super().__init__()
        self.text = text
    
    def run(self):
        emotion.extract_emotion(self.text)

class Ttser(threading.Thread):
    def __init__(self, text):
        super().__init__()
        self.text = text
    
    def run(self):
        tts.make_tts(self.text)

def conversation():
    # input("엔터 입력하여 음성 입력 시작.")
    # user_input = stt.stting() # STT로 구현
    
    # if not user_input: # STT 실패 대비
    #     print("음성 인식 실패")
    #     return
    
    # print(f"아부: {user_input}")
    user_input = input("아부: ")

    april_res = gemini.chat(user_input, mem.get_context())
    print(f"에이프릴: {april_res}")
    # emotioner = Emotioner(april_res)
    # emotioner.start()
    emotion.extract_emotion(april_res)
    # ttser = Ttser(april_res)
    # ttser.start()
    tts.make_tts(april_res)
    mem.append_to_context(f"아부: {user_input}\n에이프릴: {april_res}")

if __name__ == "__main__":
    profiler = Profiler()
    while True:
        conversation()
        if not profiler.is_alive():
            profiler = Profiler()
            profiler.start()