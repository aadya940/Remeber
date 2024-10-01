from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatButton, MDRaisedButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDIconButton, MDFillRoundFlatIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog

from kivy.core.window import Window

from .write_notes import WriteNotesScreen
from .contacts import ContactsScreen
from .login import LoginScreen
from .ask_ai import ChatScreen

import os


class RememberApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_hue = "A400"

        self.screen_manager = MDScreenManager()

        home_screen = MDScreen(name="home")

        login_screen = LoginScreen(name="login")
        self.screen_manager.add_widget(login_screen)
        self.screen_manager.add_widget(home_screen)

        _login = self.screen_manager.get_screen("login")

        if _login.check_existing_info():
            self.screen_manager.current = "home"  # Go to the main screen if info exists
            os.environ["GEMINI_API_KEY"] = _login.check_existing_info()[0]
        else:
            self.screen_manager.current = "login"  # Go to the login screen

        chat_screen = ChatScreen(name="chat")
        self.screen_manager.add_widget(chat_screen)

        notes_screen = WriteNotesScreen(name="notes")
        self.screen_manager.add_widget(notes_screen)

        contacts_screen = ContactsScreen(name="contacts")
        self.screen_manager.add_widget(contacts_screen)

        title_label = MDLabel(
            text="[b]Remember your People using[/b]\n[i] the Remember App[/i]",
            markup=True,
            font_style="H4",
            pos_hint={"center_x": 0.65, "top": 1.3},
            halign="left",
        )

        add_human_btn = MDIconButton(
            icon="pencil",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            pos_hint={"center_x": 0.8, "center_y": 0.1},
            icon_size=80,
            on_release=lambda x: self.switch_to_notes(),
        )

        ask_ai_btn = MDFillRoundFlatIconButton(
            text="[b]Ask AI[/b]",
            font_style="H4",
            theme_text_color="Custom",
            md_bg_color=self.theme_cls.primary_color,  # Filled background color
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            size_hint=(0.6, 0.1),
            on_release=lambda x: self.switch_to_chat(),
        )

        contact_list_btn = MDIconButton(
            icon="account",
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            pos_hint={"center_x": 0.6, "center_y": 0.1},
            icon_size=80,
            on_release=lambda x: self.switch_to_contacts(),
        )

        home_screen.add_widget(title_label)
        home_screen.add_widget(add_human_btn)
        home_screen.add_widget(contact_list_btn)
        home_screen.add_widget(ask_ai_btn)

        Window.bind(on_keyboard=self.on_back_button)

        return self.screen_manager

    def switch_to_notes(self):
        self.screen_manager.current = "notes"

    def switch_to_chat(self):
        self.screen_manager.current = "chat"

    def switch_to_contacts(self):
        self.screen_manager.current = "contacts"

    def on_back_button(self, window, key, *args):
        if key == 27:
            if self.screen_manager.current != "home":
                self.screen_manager.current = "home"
                return True
        return False


RememberApp().run()
