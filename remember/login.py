from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFillRoundFlatButton
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.uix.screenmanager import Screen

import sqlite3
import os


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

        # Main layout for the screen
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        # Gemini API Key Label
        self.api_label = MDLabel(
            text="[b]Google Gemini API Key[/b]",
            markup=True,
            halign="center",
            font_style="H5",
        )

        # Gemini API Key Input
        self.api_input = MDTextField(
            hint_text="Enter Google Gemini API KEY",
            multiline=False,
            size_hint_y=None,
            height="40dp",
            mode="rectangle",
            radius=[10, 10, 10, 10],
            font_size="16sp",
            required=True,
        )

        # Name Label
        self.name_label = MDLabel(
            text="[b]What's your name?[/b]",
            markup=True,
            halign="center",
            font_style="H5",
        )

        # Name Input
        self.name_input = MDTextField(
            hint_text="Enter your name",
            multiline=False,
            size_hint_y=None,
            height="40dp",
            mode="rectangle",
            radius=[10, 10, 10, 10],
            font_size="16sp",
            required=True,
        )

        # Submit Button
        self.submit_button = MDFillRoundFlatButton(
            text="Save",
            size_hint=(None, None),
            size=("200dp", "50dp"),
            font_size="16sp",
            on_press=self.on_submit,
            pos_hint={"center_x": 0.5},
        )

        # Add widgets to layout with padding and spacing
        self.layout.add_widget(self.api_label)
        self.layout.add_widget(self.api_input)
        self.layout.add_widget(self.name_label)
        self.layout.add_widget(self.name_input)
        self.layout.add_widget(self.submit_button)

        # Add layout to the screen
        self.add_widget(self.layout)

        # Database setup for Android and other platforms
        if platform == "android":
            from android.storage import app_storage_path

            self.login_db_path = os.path.join(app_storage_path(), "./login_info.db")
        else:
            self.login_db_path = "./login_info.db"

        self.conn = sqlite3.connect(self.login_db_path)
        self.cursor = self.conn.cursor()
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS login_info (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            api_key TEXT NOT NULL,
                            name TEXT NOT NULL
                            )"""
        )
        self.conn.commit()

    def check_existing_info(self):
        self.cursor.execute("SELECT api_key, name FROM login_info")
        return self.cursor.fetchone()

    def on_submit(self, instance):
        api_key = self.api_input.text
        name = self.name_input.text

        if self.validate(api_key, name):
            self.store_info(api_key, name)
            self.manager.current = "home"  # Navigate back to the main screen
        else:
            self.api_input.text = ""
            self.name_input.text = ""

    def validate(self, api_key, name):
        return api_key != "" and name != ""

    def store_info(self, api_key, name):
        self.cursor.execute(
            "INSERT INTO login_info (api_key, name) VALUES (?, ?)", (api_key, name)
        )
        self.conn.commit()

    def close_db(self):
        self.conn.close()
