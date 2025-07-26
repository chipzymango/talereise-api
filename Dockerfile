FROM python:3.8-slim-bookworm

WORKDIR /code

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt


RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./app /code/app

EXPOSE 8000

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
