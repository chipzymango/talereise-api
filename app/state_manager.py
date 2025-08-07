import openai
import json
from app.dialog_manager import DialogState
from app.post_processing import correct_stop_place
from app.api_service import get_stop_id, get_next_departure
from app.stop_loader import load_stop_names

session_states = {}

stop_list = load_stop_names()

def get_state(session_id): # session id is unique key to identify the user's session
    if session_id in session_states:
        return session_states[session_id] # DialogState object
    else:
        state = DialogState()
        session_states[session_id] = state
        return state
    
def llm_fill_state(user_input, state): # take user input and current state and return a dict form of 
    system_prompt = f"""
    Du er en llm i en kollektivtransport-taleassistent app som hjelper brukeren med å finne kollektivtransportinformasjon, på samme måte som man kan gjøre i Ruter- eller Entur-appen. Du skal holde styr på denne multi-domain dialogue state tracking samtalen.
    Din jobb er å systematisk identifisere og holde styr på brukerens mål (goal) og den tilleggsinformasjonen (slots) som kreves for å nå målet, gjennom hele samtalen.

    Gjør følgende:
    1. Les først 'user' og 'system' nøklene i 'history'-dictonaryen for å få kontekst om samtalen i tilfelle dette er en pågående samtale
    2. Les og forstå brukerens spørsmål
    3. Returner et JSON-objekt med følgende:
    * goal: Brukerens mål eller hensikt med spørsmålet. Akkurat nå skal du kun gjenkjenne "get_departure", altså spørsmål som handler om henting av avgangstider.
    * slots: En dict som består av 'origin', 'line_number', 'direction'. For hvert av disse nøklene, skal verdien enten være informasjonen som brukeren har gitt i sitt spørsmål, eller null hvis brukeren ikke har oppgitt den informasjon. Eksempel: "Når kommer 23 Olavsgaard på Ås" så vil ofte Olaavsgard være retningen her.
    * missing_slots: En liste med navnene på alle slots i slots som har verdien null, (altså den tilleggsinformasjone som mangles fra bruker)
    * history: en liste av dict der hvert element har nøklene "role" ('user' eller 'system`) og "text" (meldingen). Denne listen skal være samtalehistorikken av samtalen mellom brukeren og systemet og skal sørge for å bygge kontekst for videre samtale.
    * reply_context: en dict over relevant nøkkelord / data som er hentet fra entur api responsen som appen selv (og ikke du som llm) skal legge til, for å gi deg som llm kontekst når du i et senere tidspunkt skal lage et svar/tilbakemelding til brukeren.
    4. For history og reply_context skal du ikke legge til eller endre noe, bare ta det med videre.

    Tips: Hvis setningen er på en form som er slik at "nå" egentlig burde vært "når" pga. mistrankribering på openai whisper api sin side, så kan du tolke "nå" som "når" (Husk at user input er et spørsmål til syvende og sist)

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
        system_prompt = f"""
        Du er en LLM i en kollektivtransport-taleassistentapp som hjelper sluttbruker med å finne avgangstider på samme måte som i Ruter- eller Entur-appen.

        Du har mottatt en dialog state. Følg disse stegene nøyaktig:

        1. Se i 'history' -> 'user' for å finne hva sluttbrukeren spurte om.
        2. I 'reply_context' -> 'departure_time' finnes det en streng som enten er en avgangstid i form av antall gjenstående minutter, eller er en begrunnelse til at ønsket tid ikke ble funnet.
        3. Hvis det er et nummer så er det antall gjenstående minutter som du skal fortelle brukeren. Hvis ikke er det en annen beskjed og dette forklarer du til brukeren kort.
        4. Aldri nevn ord som "buss" eller "t-bane" i svaret ditt siden det er usikkert hva slags transportmiddel det snakkes om.

        Her er dialogstaten:
        {state.to_json()}
        """

        chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt}
        ]
        )
        llm_response = str(chat_completion.choices[0].message.content.strip())

        return llm_response
        
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
        llm_response = str(chat_completion.choices[0].message.content.strip())

        return llm_response

def process_state(state): # this is where the system checks and potentially performs api requests
    if state.goal == "get_next_departure":
        # attempt to correct misintepretations of names of places
        if state.slots["origin"] != "null":
            state.slots["origin"] = correct_stop_place(state.slots["origin"], stop_list)
        if state.slots["destination"] != "null":
            state.slots["destination"] = correct_stop_place(state.slots["destination"], stop_list)

    if state.is_ready():
        if state.goal == "get_departure":
            # if ready, get all slots that are required by the identified goal and perform requests with this information            
            line_number = state.slots["line_number"]
            departure_stop = correct_stop_place(state.slots["origin"], stop_list) # correct possible misinterpretations of norwegian stop place names
            front_text = correct_stop_place(state.slots["direction"], stop_list)

            stop_id = get_stop_id(departure_stop)
            departure_time = get_next_departure(stop_id, line_number, front_text)

            # the actual returned entur data added to dialog state in reply_context field, 
            # to be used by llm when it builds the response presenting the data to end user
            state.reply_context["departure_time"] = departure_time

    return state

def finalize_state(state, user_input, system_reply):
    if state.is_ready():
        state.clear_state()
    else:
        state.log_turn(user_input=user_input, system_reply=system_reply) 