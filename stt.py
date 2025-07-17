import speech_recognition as sr
import gemini

recognizer = sr.Recognizer()

def stting():
    with sr.Microphone() as source:
        print("지금 말하시오")
        audio = recognizer.listen(source)
    wav = audio.get_wav_data()
    # with open("stt.wav", 'wb') as f:
    #     f.write(wav)
    return gemini.stting(wav)