import time

context = ""

log_file = f"logs/{time.time()}.txt"
tmp = open(log_file, "w", encoding="utf-8")
tmp.close()

def append_to_context(text):
    global context
    context += f"{text}\n"
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(f"{text}\n")

def get_context():
    return context