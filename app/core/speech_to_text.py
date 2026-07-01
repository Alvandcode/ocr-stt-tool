import speech_recognition as sr


def audio_to_text(audio_path: str, lang: str = "fa-IR") -> str:
    """
    Convert speech in an audio file to text using Google Web Speech API.
    """
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)
    text = r.recognize_google(audio, language=lang)
    return text.strip()
