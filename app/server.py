from fastapi import FastAPI, UploadFile, File
from transformers import BertTokenizerFast, BertForTokenClassification  
import os, openai, tempfile
from process_ner import correct_stop_place
from fetch_stops import fetch_stop_names

stop_list = fetch_stop_names("oslo_akershus_stops_export")

# use whisper api for now
openai.api_key = os.getenv("OPENAI_API_KEY")

# load the fine tuned NER model for extracting specific entities from the text returned from transcription and its tokenizer
ner_model  = BertForTokenClassification.from_pretrained("chipzy/bert-base-no-akershus-transit-ner")
ner_tokenizer = BertTokenizerFast.from_pretrained("chipzy/bert-base-no-akershus-transit-ner")
ner_label_mapping = {0: "O", 1: "B-ROUTENUMBER", 2: "B-ROUTENAME", 3: "I-ROUTENAME", 4: "B-STOPPLACE", 5: "I-STOPPLACE"}

app = FastAPI()

@app.get("/")
def root():
    return {"message": "TaleReise APIs"}

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    # ------------------ ASR MODEL: receive audio file, run Whisper, return text
    # create a tempfile that whisper can read from  
    # Whisper will use ffmpeg under the hood, which needs a file path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read()) # UploadFile.read() method is async
        tmp.flush() # make sure everything is written to disk
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        result = openai.Audio.transcribe("whisper-1", f, response_format="text", language="no")
        print("result: " + str(result))

    text = result.replace(".", "") # temp fix to ensure model doesn't assign . as route number. model needs to be fine tuned further to fix this at some point

    # ------------------ NER MODEL: receive text, return entities
    route_name, route_number, stop_place = "", "", ""

    inputs = ner_tokenizer(text, return_tensors="pt")

    outputs = ner_model(**inputs)
    predictions = outputs.logits.argmax(dim=-1)

    predicted_tags = [ner_label_mapping[label_id.item()] for label_id in predictions[0]]

    # convert token ids back to words
    tokens = ner_tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        
    # merge the subwords
    merged_tokens = []
    merged_tags = []

    for token, tag in zip(tokens, predicted_tags):
        if token.startswith("##"):
            merged_tokens[-1] += token[2:] # add the subword to previous token
        elif token in ["[CLS]", "[SEP]", "[PAD]"]: 
            continue # ignore these special tokens
        else:
            merged_tokens.append(token)
            merged_tags.append(tag)

    for token, tag in zip(merged_tokens, merged_tags): # merged_tokens meaning merged after possible split-ups of tokens in tokenization
        if tag == "B-ROUTENAME" or tag == "I-ROUTENAME":
            route_name = route_name + " " + token
        elif tag == "B-ROUTENUMBER":
            route_number = token
        elif tag == "B-STOPPLACE" or tag == "I-STOPPLACE":
            stop_place = stop_place + " " + token

    if stop_place != "":
        # attempt to correct Whisper pronunciation mistakes in norwegian stop place names
        stop_place = correct_stop_place(stop_place, stop_list)

    if route_name == "":
        route_name = "token not found"
    if stop_place == "":
        stop_place = "token not found"
    if route_number == "":
        route_number = "token not found"

    data = {'data': {
        'route_number': route_number,
        'route_name': route_name,
        'stop_place': stop_place
    }}

    return {'recognized_data': data}