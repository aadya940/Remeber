import os
from google import generativeai

from prompt import generate_prompt


def setup_gemini():
    user_gemini_api = os.environ["GEMINI_API_KEY"]
    generativeai.configure(api_key=user_gemini_api)


def get_ai_suggestions(name, label, notes, _max_output_tokens=200):
    """To be called after `setup_gemini`."""
    model = generativeai.GenerativeModel("gemini-1.5-flash")
    _generation_config = generativeai.GenerationConfig(
        max_output_tokens=_max_output_tokens,
    )
    prompt = generate_prompt(name, label, notes)
    response = model.generate_content(prompt, generation_config=_generation_config)
    return response.text
