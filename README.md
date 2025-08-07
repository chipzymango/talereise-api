# TaleReise API

An API for a potential speech-assistant TaleReise to handle questions from audio input about departure times of public transport through AI models.

<p align="center">
    <img src='./img/talereise.png?'>
</p>

## Features

- Transcription of Norwegian speech to text via OpenAI's Whisper
- Conversation handling through the concept of Dialog state tracking (DST)
- Recognition of user intents with the help of AI reasoning
- Utilizing Entur's API services to fetch the desired data (Currently Ruter-operated vehicles in Oslo are supported for now)
- A natural user experience through LLM generated responses.

---

## Prerequisites

- Python 3.8+
- Docker (optional)  
- OpenAI API key (An API-key from OpenAI is necessary to be able to perform requests to the Whisper and GPT models)

---

## Getting started

1. Clone the repo  
   ```bash
   git clone https://github.com/chipzymango/talereise-api.git
   cd talereise-api


2. Install the dependencies required
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    

3. Export the API key:

    ```bash
    export OPENAI_API_KEY="api key"
    ```

    or in Powershell:
    ```powershell
    setx OPENAI_API_KEY="api key"
    ```

4. Start server locally
    ```bash
    uvicorn app.server:app --reload --host 0.0.0.0 --port 8000
    ```


5. Test with audio input through Swagger UI at localhost:8000/docs