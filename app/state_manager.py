import openai
import json
from dialog_manager import DialogState

session_states = {}

def get_state(session_id): # session id is unique key to identify the user's session
    if session_id in session_states:
        return session_states[session_id] # DialogState object
    else:
        state = DialogState()
        session_states[session_id] = state
        return state
    
def get_updated_state(user_input, state): # take user input and current state and return a dict form of 
    system_prompt = f"""
    Du er en llm i en kollektivtransport-taleassistent app som er laget for å kunne finne fram til kollektivreise-relatert info, liknende den type info man kan finne på Ruter / Entur appen. 
    Din jobb er å systematisk identifisere og holde styr over brukerens mål og den tilleggsinformasjonen (slots) som kreves for å nå ønsket mål. 
    Returner alltid kun et JSON-objekt med oppdatert dialog-state med:
    - goal: nåværende mål (et eget mål du selv lager basert på hva du tror brukeren ønsker å oppnå)
    - slots: dict med slot navn og verdier, eller null hvis ikke oppgitt.
    - history: dict som består av 
    
    Nåværende dialog state:
    {state.to_json()}
    """

    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ] # gpt response will be based off of the prompt and user input
    )
    llm_response = chat_completion.choices[0].message.content.strip()

    # parse the returned json object to dict so it can be read easier
    updated_state_dict = json.loads(llm_response)

    # update the current state with the new state returned from llm in dict form
    state.goal = updated_state_dict.get("goal")
    state.slots = updated_state_dict.get("slots", {})
    state.missing_slots = [k for k, v in state.slots.items() if v is None] # list of unidentified slots (f.ex. goal requires destination but not destination is not defined by user)

    return state # return the state with the new data 