import simpleaudio as sa

wav = sa.WaveObject.from_wave_file("tts.wav")
pla = wav.play()
for i in range(10000):
    print(i)
print("d아니")