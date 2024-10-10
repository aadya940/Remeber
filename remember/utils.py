import re

from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFillRoundFlatIconButton

from contacts import ContactsScreen


def convert_markdown_to_kivy_markup(text):
    # Convert markdown bold (**) to Kivy markup [b] for bold
    text = re.sub(r"\*\*(.*?)\*\*", r"[b]\1[/b]", text)
    # Convert markdown italic (*) to Kivy markup [i] for italic
    text = re.sub(r"\*(.*?)\*", r"[i]\1[/i]", text)

    text = re.sub(r"^\*\s*", "• ", text, flags=re.MULTILINE)
    return text


class ContactFilterScreen(MDScreen):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.theme_cls.theme_style = "Light"

        meetings_btn = MDFillRoundFlatIconButton(
            text="Meetings",
            icon="pencil",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            md_bg_color=self.theme_cls.primary_color,
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.switch_to_meetings(),
        )

        conversations_btn = MDFillRoundFlatIconButton(
            text="Conversations",
            icon="pencil",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            md_bg_color=self.theme_cls.primary_color,
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.switch_to_conversations(),
        )

        self.add_widget(meetings_btn)
        self.add_widget(conversations_btn)

    def switch_to_meetings(self):
        self.screen_manager.current = "contacts_meetings"

    def switch_to_conversations(self):
        self.screen_manager.current = "contacts"
