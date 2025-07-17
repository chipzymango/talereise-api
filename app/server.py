import os, openai
from fastapi import FastAPI, UploadFile, File
from transcription import transcribe_audio
from state_manager import get_state

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/")
def root():
    return {"message": "TaleReise API"}

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...), session_id = "test_session"):
    transcribed_text = await transcribe_audio(file)
    state = get_state(session_id)
    return {
        "No errors yet!"
    }