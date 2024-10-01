from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.core.window import Window

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager

import sqlite3


class ChatBubble(MDCard):
    def __init__(self, message, sender="user", **kwargs):
        super().__init__(**kwargs)

        self.size_hint_y = None
        self.height = dp(80)  # Increased height for zoom effect
        self.padding = dp(15)  # Increased padding for larger text
        self.radius = [20, 20, 20, 20]  # More rounded corners
        self.md_bg_color = [0, 0.6, 1, 1] if sender == "user" else [0.9, 0.9, 0.9, 1]
        self.pos_hint = {"right": 1} if sender == "user" else {"left": 1}

        # Add the label with larger text to the card
        self.add_widget(
            Label(
                text=message,
                color=(0, 0, 0, 1),
                size_hint_y=None,
                height=self.height,
                font_size=dp(20),
            )
        )


class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._name = "Human"  # Default name in case the DB query fails

        # Try connecting to the database and fetching the user's name
        try:
            self.db = sqlite3.connect("login_info.db")
            self.cursor = self.db.cursor()

            self.cursor.execute("SELECT name FROM login_info LIMIT 1")
            result = self.cursor.fetchone()
            if result:
                self._name = result[0]  # Assign the fetched name
            self.db.close()

        except Exception as e:
            print(f"Database error: {e}")
            # Database error fallback

        # Root layout for the screen
        root_layout = BoxLayout(orientation="vertical")

        # Scrollable chat area
        self.scroll_view = ScrollView(
            do_scroll_x=False, do_scroll_y=True, size_hint=(1, 0.85)
        )
        self.chat_layout = MDBoxLayout(
            orientation="vertical", padding=dp(20), spacing=dp(20), size_hint_y=None
        )  # Larger padding and spacing
        self.chat_layout.bind(minimum_height=self.chat_layout.setter("height"))

        self.scroll_view.add_widget(self.chat_layout)
        root_layout.add_widget(self.scroll_view)

        # Bottom input bar layout
        input_layout = BoxLayout(
            size_hint_y=None, height=dp(80), padding=dp(10)
        )  # Larger input box and padding

        # Text input for user message (increased size)
        self.user_input = TextInput(
            hint_text=f"Who are you going to talk to, {self._name}?",
            size_hint_x=0.85,
            multiline=False,
            font_size=dp(20),
        )
        self.user_input.bind(on_text_validate=self.send_message)

        # Send button (increased size)
        send_button = Button(text="Send", size_hint_x=0.15, font_size=dp(20))
        send_button.bind(on_release=lambda x: self.send_message())

        input_layout.add_widget(self.user_input)
        input_layout.add_widget(send_button)
        root_layout.add_widget(input_layout)

        # Add the root layout to the screen
        self.add_widget(root_layout)

    def send_message(self, *args):
        # Get user message from input box
        message = self.user_input.text.strip()

        if message:
            # Add user message to chat layout
            self.add_chat_bubble(message, sender="user")

            # Simulate AI response
            ai_message = f"AI response to: {message}"
            self.add_chat_bubble(ai_message, sender="ai")

        # Clear input after sending
        self.user_input.text = ""

    def add_chat_bubble(self, message, sender="user"):
        bubble = ChatBubble(message=message, sender=sender)
        self.chat_layout.add_widget(bubble)

        # Scroll to bottom after adding the new message
        self.scroll_view.scroll_y = 0
