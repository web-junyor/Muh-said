from gtts import gTTS
import uuid
import os


def text_to_voice(text: str, lang: str) -> str:
    filename = f"voice_{uuid.uuid4()}.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    return filename
