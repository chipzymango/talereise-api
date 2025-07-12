import os, openai
from fastapi import FastAPI, UploadFile, File
from transcription import transcribe_audio
from entity_extraction import extract_entities

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/")
def root():
    return {"message": "TaleReise API"}

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    transcribed_text = await transcribe_audio(file)
    entities = extract_entities(transcribed_text)
    #reise_data = request_data(entities)
    #final_response = create_response(reise_data)
    print(f"llm-respons: {entities}")

    return {
        "transcribed_text": transcribed_text,
        "structured_data": entities
    }