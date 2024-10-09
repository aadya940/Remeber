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

from api_calls import setup_gemini, start_chat, send_first_message, send_message
from utils import convert_markdown_to_kivy_markup

import sqlite3


class ChatBubble(MDCard):
    def __init__(self, message, sender, **kwargs):
        super().__init__(**kwargs)

        self.size_hint_y = None
        self.padding = dp(15)  # Padding around the text
        self.radius = [20, 20, 20, 20]  # Rounded corners
        self.md_bg_color = [0, 0.6, 1, 1] if sender != "AI" else [0.9, 0.9, 0.9, 1]
        self.pos_hint = {"right": 1} if sender != "AI" else {"left": 1}

        # Create the label with the text
        self.label = Label(
            text=message,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            font_size=dp(20),
            text_size=(
                Window.width - dp(60),
                None,
            ),  # Ensure text wraps inside the card
            halign="left",  # Align text to the left
            valign="middle",  # Vertical alignment
            markup=True,
        )
        self.label.bind(
            texture_size=self._update_height
        )  # Bind to dynamically adjust height

        # Add the label to the card
        self.add_widget(self.label)

    def _update_height(self, *args):
        # Set the height of the card based on the label's content
        self.height = self.label.texture_size[1] + dp(30)  # Add padding for the card
        self.label.height = self.label.texture_size[
            1
        ]  # Adjust label height to fit text


class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._name = "Human"  # Default name in case the DB query fails
        self._prompt_args = {}
        self._label_items = []
        self.i = 0  # Index for label items

        try:
            self.notes_db = sqlite3.connect("notes.db")
            self.notes_cursor = self.notes_db.cursor()

        except Exception as e:
            print(f"Database error: {e}")
            # Database error fallback

        # Try connecting to the database and fetching the user's name
        try:
            self.db = sqlite3.connect("./login_info.db")
            self.cursor = self.db.cursor()

            self.cursor.execute("SELECT name FROM login_info LIMIT 1")
            result = self.cursor.fetchone()
            if result:
                self._name = result[0]  # Assign the fetched name

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
            self.add_chat_bubble(message, sender=f"{self._name}")

            # Step 1: Asking for the user's name
            if not self._prompt_args:
                self._prompt_args["Name"] = message.lower()

                # Simulate AI response
                ai_message = f"Name received: {message}"
                self.add_chat_bubble(ai_message, sender="AI")

                # Check if the notes table exists and query labels
                try:
                    self.notes_cursor.execute(
                        "SELECT label FROM notes WHERE LOWER(title) = ?",
                        (self._prompt_args["Name"],),
                    )
                    self._label_items = self.notes_cursor.fetchall()

                    if self._label_items:  # If labels exist for the provided name
                        self.i = 0
                        self._label = self._label_items[self.i][0]
                        ai_message = f'Is it {message} related to you by "{self._label}" Contact?'
                        self.add_chat_bubble(ai_message, sender="AI")
                        self.user_input.hint_text = "Yes or No?"
                    else:
                        # If no labels are found for the given name
                        ai_message = f"No labels found for the name {self._prompt_args['Name']}. Please enter a valid label."
                        self.add_chat_bubble(ai_message, sender="AI")
                        del self._prompt_args["Name"]  # Reset to ask for the name again
                        self.user_input.hint_text = (
                            f"Who are you going to talk to, {self._name}?"
                        )

                except sqlite3.OperationalError:
                    # This exception indicates that the notes table doesn't exist
                    ai_message = (
                        f"Hey {self._name}, you haven't started writing any notes yet."
                    )
                    self.add_chat_bubble(ai_message, sender="AI")
                    del self._prompt_args["Name"]  # Reset to ask for the name again
                    self.user_input.hint_text = (
                        f"Who are you going to talk to, {self._name}?"
                    )

                self.user_input.text = ""
                return

            # Step 2: Asking to confirm the label
            elif "Name" in self._prompt_args and "Label" not in self._prompt_args:
                if "yes" in message.lower():
                    self._prompt_args["Label"] = self._label
                    ai_message = f"Label confirmed: {self._label}"
                    self.add_chat_bubble(ai_message, sender="AI")
                    self.user_input.text = ""
                    ai_message = "Generating AI Recommendations ..."
                    self.add_chat_bubble(ai_message, sender="AI")
                    # No need to commit for SELECT queries, so removed the commit
                    self.notes_cursor.execute(
                        """SELECT content FROM notes WHERE LOWER(title) = ? AND LOWER(label) = ?""",
                        (
                            self._prompt_args["Name"].lower(),
                            self._prompt_args["Label"].lower(),
                        ),
                    )
                    result = self.notes_cursor.fetchone()
                    if result:
                        self._prompt_args["Content"] = result[0]
                        self.user_input.hint_text = ""
                        self._model = setup_gemini()

                        self._chat = start_chat(self._model)

                        _suggestions = send_first_message(
                            self._chat,
                            self._prompt_args["Name"],
                            self._prompt_args["Label"],
                            self._prompt_args["Content"],
                        )

                        _suggestions = convert_markdown_to_kivy_markup(
                            _suggestions.text
                        )
                        self.add_chat_bubble(_suggestions, sender="AI")
                    else:
                        self.add_chat_bubble(
                            "No content found for the selected label.", sender="AI"
                        )

                else:
                    self.i += 1
                    if self.i < len(self._label_items):
                        self._label = self._label_items[self.i][0]
                        ai_message = f"Is it {message} from {self._label}?"
                        self.add_chat_bubble(ai_message, sender="AI")
                        self.user_input.hint_text = "Yes or No?"
                    else:
                        ai_message = f"{self._name}, that's all for the name {self._prompt_args['Name']}."
                        self.add_chat_bubble(ai_message, sender="AI")
                        del self._prompt_args["Name"]  # Reset to ask for the name again
                        self.user_input.hint_text = (
                            f"Who are you going to talk to, {self._name}?"
                        )
                return

            elif "Name" in self._prompt_args and "Label" in self._prompt_args:
                _suggestions = send_message(self._chat, message)
                self.add_chat_bubble(_suggestions.text, sender="AI")

        # Clear input after sending
        self.user_input.text = ""

    def query_labels(self, name):
        """Query database for labels associated with the given name."""
        try:
            self.notes_db = sqlite3.connect("notes.db")
            self.notes_cursor = self.notes_db.cursor()
            self.notes_cursor.execute(
                "SELECT label FROM notes WHERE LOWER(title) = ?", (name,)
            )
            self._label_items = [item[0] for item in self.notes_cursor.fetchall()]

        except Exception as e:
            print(f"Database error: {e}")

    def add_chat_bubble(self, message, sender="user"):
        bubble = ChatBubble(message=message, sender=sender)
        self.chat_layout.add_widget(bubble)

        # Scroll to bottom after adding the new message
        self.scroll_view.scroll_y = 0
