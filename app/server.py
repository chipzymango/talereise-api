import os, openai
from fastapi import FastAPI, UploadFile, File
from app.transcription import transcribe_audio
from app.state_manager import get_state, llm_fill_state, create_response, process_state, finalize_state
from app.dialog_manager import DialogState

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

@app.get("/")
def root():
    return {"message": "TaleReise API"}

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...), session_id = "test_session"):

    transcribed_text = await transcribe_audio(file) # transcribe user speech to text
    state = get_state(session_id) # create or retrieve a dialog state to keep track of the conversation
    updated_state = llm_fill_state(transcribed_text, state) # update current state with the new state data returned/filled by llm
    processed_state = process_state(updated_state) # process the updated state by checking if it's ready and return the state with updated reply_context
    system_reply = create_response(processed_state) # generate llm response based on the updated state
    finalize_state(state, transcribed_text, system_reply) # register user input and system response to state to build conversation historyy 

    return {
        "reply": system_reply
    }