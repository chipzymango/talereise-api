import openai
import json
from app.dialog_manager import DialogState

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
    Du er en llm i en kollektivtransport-taleassistent app som hjelper brukeren med å finne kollektivtransportinformasjon, på samme måte som man kan gjøre i Ruter- eller Entur-appen.  
    Din jobb er å systematisk identifisere og holde styr på brukerens mål (goal) og den tilleggsinformasjonen (slots) som kreves for å nå målet.  

    Returner alltid kun et JSON-objekt med:
    - goal: Brukerens nåværende mål Dette skal alltid være enten 'plan_journey' eller 'get_next_departure'. Hvis usikker, sett goal til unknown
    - slots: dict med slot navn og verdier, eller null hvis ikke oppgitt.
    - missing_slots: En liste med navnene på alle slots i slots har verdien null. (altså den tilleggsinformasjone som mangles fra bruker)

    For hvert goal som velges må spesifikke slots fylles ut:
    - 'plan_journey': krever slots: 'origin', 'destination'
    - 'get_next_departure': krever slots: 'line_number', 'origin'
    - 'find_stop': krever slot: 'stop_name'
    - history: dict der hvert element har nøklene "role" ('user' eller 'system`) og "text" (meldingen).
    Denne listen skal inneholde alle tidligere meldinger i dialogen, både fra bruker og system. Skal sørge for å bygge kontekst for videre samtale.
    du skal ikke legge til noe her, bare returnere den eksisterende listen.
    du skal ikke fylle opp slots med informasjon som ikke er oppgitt av brukeren. Altså, hvis brukeren ikke har oppgitt verdien for en slot, skal verdien være null.
    
    # Bruker spørsmål: 
    {user_input}

    # Nåværende dialog-state:
    {state.to_json()}
    """

    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt}
        ] # gpt response will be based off of the prompt
    )
    llm_response = chat_completion.choices[0].message.content

    updated_state_dict = json.loads(llm_response)

    # update the current state with the new state returned from llm in dict form
    state.goal = updated_state_dict.get("goal")
    state.slots = updated_state_dict.get("slots", {})
    state.missing_slots = [k for k, v in state.slots.items() if v is None] # list of unidentified slots (f.ex. goal requires destination but not destination is not defined by user)

    return state # return the state with the new data

def create_response(state):
    if state.is_ready():
        return "All info needed (no missing slots), ready to perform requests."
    else:
        system_prompt = f"""
        Du er en llm i en kollektivtransport-taleassistent app som hjelper brukeren med å finne kollektivtransportinformasjon, på samme måte som man kan gjøre i Ruter- eller Entur-appen.
        Du har fått en dialog state som inneholder brukerens mål og tilleggsinformasjon (slots) som kreves for å nå ønsket mål. Her finnes det noen missing slots, altså nødvendig informasjon som brukeren ikke har oppgitt for å kunne nå målet.
        Returner en høflig men veldig kort forespørsel til brukeren om å oppgi den manglende informasjonen som ligger i missing_slots i dialog staten:
        Nåværende dialog state:
        {state.to_json()}
        """

        chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=1,
        messages=[
            {"role": "system", "content": system_prompt}
        ]
        )
        llm_response = chat_completion.choices[0].message.content.strip()

        return str(llm_response)