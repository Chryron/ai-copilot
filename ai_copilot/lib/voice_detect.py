
TRANSCRIPT_PATH = '/mnt/c/Users/Nazmus/coding-home/speech/transcript.txt'
AUDIO_PATH = '/mnt/c/Users/Nazmus/coding-home/speech/audio'
# read the transcript. if it only contains the word "READY", then return False else return the contents
def read_transcript():
    with open(TRANSCRIPT_PATH, 'r') as f:
        contents = f.read()
        if 'READY' in contents:
            return False
        else:
            return contents
        
# write the word "READY" to the transcript
def write_transcript(text):
    with open(TRANSCRIPT_PATH, 'w') as f:
        f.write(text)

    
from gtts import gTTS
def save_audio(text):
    import time
    t = time.time()
    language = 'en'
    myobj = gTTS(text=text, lang=language, slow=False)
    myobj.save(AUDIO_PATH+'{}.mp3'.format(t))

