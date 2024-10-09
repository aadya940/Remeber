import os
from google import generativeai

from prompt import generate_prompt


def setup_gemini():
    user_gemini_api = os.environ["GEMINI_API_KEY"]
    generativeai.configure(api_key=user_gemini_api)
    model = generativeai.GenerativeModel("gemini-1.5-flash")
    return model


def start_chat(model):
    """To be called after `setup_gemini`."""
    chat = model.start_chat(history=[])
    return chat


def send_first_message(chat, name, label, notes):
    prompt = generate_prompt(name, label, notes)
    response = chat.send_message(prompt)
    return response


def send_message(chat, message):
    res = chat.send_message(message)
    return res
