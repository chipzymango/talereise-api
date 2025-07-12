import openai
# try and get the relevant entities through llm prompt
def extract_entities(text):
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
    return llm_response