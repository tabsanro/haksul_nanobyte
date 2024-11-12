# backend/Dockerfile

FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .

# RUN pip install -r requirements.txt
RUN pip install openai
RUN pip install SpeechRecognition
RUN pip install sentence_transformers
COPY . .

