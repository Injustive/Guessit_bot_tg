from gtts import gTTS
from tempfile import TemporaryFile

def get_voice(text):
    f = TemporaryFile()
    tts = gTTS(text, lang='en')
    tts.write_to_fp(f)
    f.seek(0)
    return f.read()
