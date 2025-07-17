import re
import pyautogui

emos = {
    "Joy": '1',
    "Angry": '2',
    "Sorrow": '3',
    "Fun": '4',
    "Gao": '5',
    "Wink": '6',
    "Cry": '7',
    "Guruguru": '-',
    "Awawa": '=',
    "Musu": 'w'
}

def extract_emotion(text):
    emo = re.search("\[(.*?)\]", text)[1]
    pyautogui.hotkey('alt', emos[emo])
    pyautogui.press('backspace')