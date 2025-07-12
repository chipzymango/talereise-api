from fastapi import FastAPI, UploadFile, File
import openai, tempfile, os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/")
def root():
    return {"message": "TaleReise LLM-based API"}

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    # transcribe sound
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp.flush()
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        whisper_result = openai.Audio.transcribe("whisper-1", f, response_format="text", language="no")

    text = whisper_result.strip()
    print(f"Transkribert tekst: {text}")

    # get relevant entities through llm prompt instead of ner
    system_prompt = """
    Du er en kollektivtransport-assistent. Brukeren stiller spørsmål om kollektivtransport.
    Returner et JSON-objekt med feltene:
    - intent: hva brukeren vil (f.eks. "get_next_departure", "get_last_departure", "get_route")
    - route_number: hvis nevnt, ellers null
    - origin_stop: hvis nevnt, ellers null
    - destination_stop: hvis nevnt, ellers null

    Eksempel på svar:
    {
      "intent": "get_next_departure",
      "route_number": "25",
      "origin_stop": "Jernbanetorget",
      "destination_stop": "Nittedal"
    }
    """
    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    )

    llm_response = chat_completion.choices[0].message.content
    print(f"LLM-respons: {llm_response}")

    return {
        "transcribed_text": text,
        "structured_data": llm_response
    }