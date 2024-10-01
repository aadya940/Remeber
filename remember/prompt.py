__all__ = ["generate_prompt"]


def generate_prompt(name, label, notes):
    gemini_initial_str = f"""
    I am related to {name} by {label} as a contact. This is some information and/or previous conversations and/or 
    previous conversation topic:
    {notes}

    Based on this generate conversation topics for me in a concise fashion.
    """
    return gemini_initial_str
