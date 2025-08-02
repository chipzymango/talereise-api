import os, openai
from fastapi import FastAPI, UploadFile, File
from app.transcription import transcribe_audio
from app.state_manager import get_state, get_updated_state, create_response
from app.api_service import get_stop_id, get_next_departure
from app.post_processing import correct_stop_place
from app.stop_loader import load_stop_names

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

stop_list = load_stop_names()

@app.get("/")
def root():
    return {"message": "TaleReise API"}

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...), session_id = "test_session"):
    transcribed_text = "Når kommer 31 bussen på Hinnerud senter."#await transcribe_audio(file) # transcribe user speech to text
    print("Transcribed text: " + str(transcribed_text))
    state = get_state(session_id) # create or retrieve a dialog state to keep track of the conversation    
    updated_state = get_updated_state(transcribed_text, state) # update current state with the updated state returned/filled by llm
    print("State: \n" + str(updated_state.to_dict()))
    if updated_state.is_ready():
        # if ready, get all slots that are required by the identified goal and perform requests with this information
        if updated_state.goal == "get_next_departure":
            line_number = updated_state.slots["line_number"]
            departure_stop = updated_state.slots["origin"]
            print("Transcribed departure_stop: " + str(departure_stop))

            # attempt to correct misintepretations of names of stop places
            new_departure_stop = correct_stop_place(departure_stop, stop_list) 
            if departure_stop != new_departure_stop:
                print("departure_stop corrected to: " + str(new_departure_stop))
                departure_stop = new_departure_stop
                updated_state.slots["origin"] = new_departure_stop
            else:
                print("departure stop not needing correction")
            
            # perform necessary requests
            stop_id = get_stop_id(departure_stop)
            departure_time = get_next_departure(stop_id, line_number)

            # the actual returned entur data added to dialog state in reply_context field, 
            # to be used by llm when it builds the response presenting the data to end user
            updated_state.reply_context["departure_time"] = departure_time
            print("Departure time at " + str(departure_stop) + ": " + str(departure_time))
        else:
            print("Ready goal not identified (what is " + str(updated_state.goal) + "?)")
    else:
        print("Not ready yet")

            #print("stop id of origin: " + str(stop_id))
    system_reply = create_response(updated_state) # llm response based on the updated state
    updated_state.log_turn(transcribed_text, system_reply) # register user input and system response to build conversation history context for llm
    
    return {
        str("LLM Response: " + system_reply)
    }