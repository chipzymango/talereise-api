import os, openai
from fastapi import FastAPI, UploadFile, File
from transcription import transcribe_audio
from state_manager import get_state, get_updated_state

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/")
def root():
    return {"message": "TaleReise API"}

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...), session_id = "test_session"):
    transcribed_text = await transcribe_audio(file) # transcribe user speech to text
    state = get_state(session_id) # create or retrieve a dialog state to keep track of the conversation    
    updated_state = get_updated_state(transcribed_text, state) # update current state with the updated state from llm

    return {
        str(updated_state.to_dict())
    }