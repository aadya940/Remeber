from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatButton, MDFillRoundFlatIconButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDIconButton
from kivy.core.window import Window

from write_notes import WriteNotesScreen
from contacts import ContactsScreen
from login import LoginScreen
from ask_ai import ChatScreen
from utils import ContactFilterScreen

import os


class RememberApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"  # Keep light theme for now
        self.theme_cls.primary_palette = "BlueGray"  # Use a modern color palette
        self.theme_cls.primary_hue = "A400"

        self.screen_manager = MDScreenManager()

        # Home screen setup
        home_screen = MDScreen(name="home")

        contact_filter_screen = ContactFilterScreen(
            self.screen_manager, name="contacts_filter"
        )

        # Login screen
        login_screen = LoginScreen(name="login")
        self.screen_manager.add_widget(login_screen)
        self.screen_manager.add_widget(home_screen)
        self.screen_manager.add_widget(contact_filter_screen)

        _login = self.screen_manager.get_screen("login")

        # If login info exists, proceed to the home screen
        if _login.check_existing_info():
            self.screen_manager.current = "home"
            os.environ["GEMINI_API_KEY"] = _login.check_existing_info()[0]
        else:
            self.screen_manager.current = "login"

        # Add the other screens
        chat_screen = ChatScreen(name="chat")
        self.screen_manager.add_widget(chat_screen)

        notes_screen = WriteNotesScreen(name="notes")
        self.screen_manager.add_widget(notes_screen)

        notes_screen_events = WriteNotesScreen(_type="event", name="notes_events")
        self.screen_manager.add_widget(notes_screen_events)

        contacts_screen = ContactsScreen(_type=None, name="contacts")
        self.screen_manager.add_widget(contacts_screen)

        contacts_screen_meetings = ContactsScreen(
            _type="event", name="contacts_meetings"
        )
        self.screen_manager.add_widget(contacts_screen_meetings)

        # Title label (styled and positioned)
        title_label = MDLabel(
            text="[b]Remember your People using[/b]\n[i]the Remember App[/i]",
            markup=True,
            font_style="H5",
            pos_hint={"center_x": 0.5, "center_y": 0.85},
            halign="center",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,  # Match primary color
        )

        # Add human button (larger size and better placement)
        add_human_btn = MDFillRoundFlatIconButton(
            text="Add Note",
            icon="pencil",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            md_bg_color=self.theme_cls.primary_color,
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.switch_to_notes(),
        )

        # Ask AI button (styled and centered)
        ask_ai_btn = MDFillRoundFlatIconButton(
            text="Ask AI",
            icon="robot",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            md_bg_color=self.theme_cls.primary_color,
            pos_hint={"center_x": 0.5, "center_y": 0.45},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.switch_to_chat(),
        )

        # Contact list button
        contact_list_btn = MDFillRoundFlatIconButton(
            text="Saved Notes",
            icon="account",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            md_bg_color=self.theme_cls.primary_color,
            pos_hint={"center_x": 0.5, "center_y": 0.3},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.switch_to_contacts(),
        )

        add_event_btn = MDFillRoundFlatIconButton(
            text="Add Event",
            icon="pencil",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            md_bg_color=self.theme_cls.primary_color,
            pos_hint={"center_x": 0.5, "center_y": 0.15},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.switch_to_event(),
        )

        # Add widgets to the home screen
        home_screen.add_widget(title_label)
        home_screen.add_widget(add_human_btn)
        home_screen.add_widget(ask_ai_btn)
        home_screen.add_widget(contact_list_btn)
        home_screen.add_widget(add_event_btn)

        # Bind back button for Android
        Window.bind(on_keyboard=self.on_back_button)

        return self.screen_manager

    def switch_to_notes(self):
        self.screen_manager.current = "notes"

    def switch_to_chat(self):
        self.screen_manager.current = "chat"

    def switch_to_contacts(self):
        self.screen_manager.current = "contacts_filter"

    def switch_to_event(self):
        self.screen_manager.current = "notes_events"

    def on_back_button(self, window, key, *args):
        if key == 27:  # Android back button
            if self.screen_manager.current != "home":
                self.screen_manager.current = "home"
                return True
        return False


if __name__ == "__main__":
    RememberApp().run()
