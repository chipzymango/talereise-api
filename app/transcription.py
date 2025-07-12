import tempfile, openai

# transcribe from audio to text
async def transcribe_audio(file):
    # create a tempfile for fastapi to work with
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp.flush()
        tmp_path = tmp.name

    # perform transcription with openai's whisper
    with open(tmp_path, "rb") as f:
        whisper_result = openai.Audio.transcribe("whisper-1", f, response_format="text", language="no")

    return whisper_result