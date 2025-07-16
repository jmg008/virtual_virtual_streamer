import gemini
import memory_manager as mem
import emotion
import threading

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

def conversation():
    user_input = input("입력하라: ") # STT로 구현
    
    # if not user_input: # STT 실패 대비
    #     print("음성 인식 실패")
    #     return
    
    # print(f"유저: {user_input}")

    april_res = gemini.chat(user_input, mem.get_context())
    print(f"에이프릴: {april_res}")
    emotioner = Emotioner(april_res)
    emotioner.start()
    mem.append_to_context(f"아부: {user_input}\n에이프릴: {april_res}")

if __name__ == "__main__":
    profiler = Profiler()
    while True:
        conversation()
        if not profiler.is_alive():
            profiler = Profiler()
            profiler.start()