import requests
import time
import playsound
import re
import os

API_TOKEN = "__pltZsebqqb6Nb7vepWpndb9mKHyaTZNsC8n8A8dwxeZ"

HEADERS = {'Authorization': f'Bearer {API_TOKEN}'}

def parser(text):
    return re.search("\[.*?\] (.*)", text)[1]

def make_wav(text):
    # get my actor
    r = requests.get('https://typecast.ai/api/actor', headers=HEADERS)
    my_actors = r.json()['result']
    my_first_actor = my_actors[0]
    my_first_actor_id = my_first_actor['actor_id']

    # request speech synthesis
    r = requests.post('https://typecast.ai/api/speak', headers=HEADERS, json={
        'text': text,
        'lang': 'auto',
        'actor_id': my_first_actor_id,
        'xapi_hd': True,
        'model_version': 'latest'
    })
    speak_url = r.json()['result']['speak_v2_url']

    # polling the speech synthesis result
    for _ in range(120):
        r = requests.get(speak_url, headers=HEADERS)
        ret = r.json()['result']
        # audio is ready
        if ret['status'] == 'done':
            # download audio file
            r = requests.get(ret['audio_download_url'])
            f = open('tts.wav', 'wb')
            f.write(r.content)
            f.close()
            return True
        else:
            # print(f"status: {ret['status']}, waiting 1 second")
            time.sleep(1)

def make_tts(text):
    text = parser(text)
    if make_wav(text):
        playsound.playsound("tts.wav")

if __name__ == "__main__":
    make_tts("아니")
    make_tts("왜안됨")