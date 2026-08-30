import os
import ollama
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:latest"
)

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

client = ollama.Client(
    host=OLLAMA_HOST
)


def ask_ai(prompt):
    if not prompt:
        raise ValueError("AI prompt is required.")

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0
        }
    )

    return response["message"]["content"].strip()