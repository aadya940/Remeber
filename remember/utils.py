import re


def convert_markdown_to_kivy_markup(text):
    # Convert markdown bold (**) to Kivy markup [b] for bold
    text = re.sub(r"\*\*(.*?)\*\*", r"[b]\1[/b]", text)
    # Convert markdown italic (*) to Kivy markup [i] for italic
    text = re.sub(r"\*(.*?)\*", r"[i]\1[/i]", text)

    text = re.sub(r"^\*\s*", "• ", text, flags=re.MULTILINE)
    return text
