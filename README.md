# TaleReise API

API for TaleReise which uses OpenAI Whisper and a fine-tuned BERT NER model to interpret route names and stops.

## Features

- Transcribe Norwegian speech to text via the OpenAI Whisper API  
- Extract route number, route name, and stop place from the transcription  
- Return structured data as JSON

---

## Prerequisites

- Python 3.8+  
- Docker (optional)  
- OpenAI API key (An API-key from OpenAI is necessary to be able to perform requests to Whisper)

---

## Getting Started

1. Clone the repo  
   ```bash
   git clone https://github.com/chipzymango/talereise-api.git
   cd talereise-api


2. Install dependencies
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

5. Test with Swagger UI at localhost:8000/docs