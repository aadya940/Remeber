from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivymd.uix.textfield import MDTextField

from kivy.uix.scrollview import ScrollView
from kivy.utils import platform
from kivy.core.window import Window

import os
import sqlite3

from write_notes import WriteNotesScreen


class ContactsScreen(MDScreen):
    def __init__(self, _type=None, **kwargs):
        super().__init__(**kwargs)
        self._type = _type

        self.theme_cls.theme_style = "Light"

        if platform == "android":
            from android.storage import app_storage_path

            self.db_path = os.path.join(app_storage_path(), "notes.db")
            if self._type == "event":
                self.db_path = os.path.join(app_storage_path(), "events.db")
        else:
            self.db_path = "./notes.db"

            if self._type == "event":
                self.db_path = "./events.db"

        # Create a ScrollView to display the contacts
        self.scroll_view = ScrollView()
        self.layout = BoxLayout(
            orientation="vertical", padding=20, spacing=20, size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter("height"))
        self.scroll_view.add_widget(self.layout)
        self.add_widget(self.scroll_view)

        # Bind the keyboard when the screen is entered
        Window.bind(on_keyboard=self.on_key_pressed)

    def on_pre_enter(self, *args):
        """Called before the screen is displayed, useful for refreshing content."""
        self.load_contacts()  # Refresh contacts each time the screen is entered

    def load_contacts(self):
        """Load contacts from the database and display them."""
        self.layout.clear_widgets()  # Clear existing contacts

        try:
            self.db = sqlite3.connect(self.db_path)
            self.cursor = self.db.cursor()

            if self._type == "event":
                self.cursor.execute("SELECT title, label FROM events")

            else:
                self.cursor.execute("SELECT title, label FROM notes")

            contacts = self.cursor.fetchall()  # Returns a list of tuples
            self.db.commit()

            if contacts:
                for contact, label in contacts:
                    card = MDCard(
                        orientation="horizontal",
                        padding=20,
                        md_bg_color=(0.9, 0.9, 0.9, 1),
                        size_hint=(
                            1,
                            None,
                        ),  # Dynamically stretch the card horizontally
                        height=200,  # Fixed height of the card
                        pos_hint={"center_x": 0.5},
                    )

                    card_layout = BoxLayout(orientation="horizontal", spacing=10)

                    # Create and add the contact label
                    contact_label = MDLabel(
                        text=f"{contact}",
                        markup=False,
                        halign="center",
                        font_style="H4",
                    )

                    card_layout.add_widget(contact_label)

                    # Create a vertical layout for the label and delete button
                    cardSmall = BoxLayout(
                        orientation="vertical",
                        size_hint=(None, None),
                        size=(200, 150),
                        spacing=10,  # Add spacing between the label and delete button
                    )

                    # Create and add the small label
                    label_small = MDLabel(
                        text=f"{label}",
                        markup=False,
                        halign="center",
                        font_style="H5",
                    )

                    delete_button = MDIconButton(
                        icon="trash-can",
                        icon_size="30sp",
                        pos_hint={"center_x": 0.5},
                        on_release=lambda btn, c=contact: self.delete_contact(c),
                    )

                    edit_button = MDIconButton(
                        icon="pencil",
                        icon_size="30sp",
                        pos_hint={"center_x": 0.5},
                        on_release=lambda btn, c=contact: self.edit_contact(c),
                    )

                    # Add the label and delete button to the vertical layout
                    cardSmall.add_widget(label_small)
                    cardSmall.add_widget(delete_button)
                    cardSmall.add_widget(edit_button)

                    # Add everything to the main card layout
                    card.add_widget(card_layout)  # Add the contact name
                    card.add_widget(cardSmall)  # Add the label and delete button

                    # Add the card to the main layout
                    self.layout.add_widget(card)

            else:
                self.layout.add_widget(
                    MDLabel(
                        text="No contacts found.",
                        markup=False,
                        halign="center",
                        font_style="H4",
                    )
                )

        except sqlite3.Error as e:
            print(f"Database error: {e}")

        finally:
            if self.db:
                self.db.close()

    def edit_contact(self, contact_title):
        try:
            self.db = sqlite3.connect(self.db_path)
            self.cursor = self.db.cursor()
            contact_title = contact_title.lower()

            if self._type == "event":
                self.cursor.execute(
                    "SELECT title, content, label FROM events WHERE LOWER(title) = ?",
                    (contact_title,),
                )
            else:
                self.cursor.execute(
                    "SELECT title, content, label FROM notes WHERE LOWER(title) = ?",
                    (contact_title,),
                )

            res = self.cursor.fetchone()
            contact_data = {
                "name": res[0],
                "notes": res[1],
                "label": res[2],
            }

            self.db.commit()

            write_notes_screen = WriteNotesScreen(
                contact=contact_data, name="writenotes"
            )

            if self.manager.has_screen("writenotes"):
                self.manager.remove_widget(self.manager.get_screen("writenotes"))

            self.manager.add_widget(write_notes_screen)
            self.manager.current = "writenotes"

        except sqlite3.Error as e:
            print(f"Database error: {e}")

        finally:
            if self.db:
                self.db.close()

    def delete_contact(self, contact_title):
        """Delete a contact from the database and refresh the contact list."""
        try:
            # Connect to the database
            self.db = sqlite3.connect(self.db_path)
            self.cursor = self.db.cursor()

            # Delete the contact
            if self._type == "event":
                self.cursor.execute(
                    "DELETE FROM events WHERE title = ?", (contact_title,)
                )
            else:
                self.cursor.execute(
                    "DELETE FROM notes WHERE title = ?", (contact_title,)
                )

            self.db.commit()

            # Refresh the contact list
            self.load_contacts()

        except sqlite3.Error as e:
            print(f"Database error: {e}")

        finally:
            if self.db:
                self.db.close()

    def on_key_pressed(self, window, key, scancode, codepoint, modifiers):
        """Handle back key (Android) or Esc key (Laptop) press."""
        if key == 27:  # Back key on Android or Esc key on Laptop
            self.load_contacts()  # Reload contacts
            return True  # Prevent default behavior (going back)
        return False

    def on_leave(self):
        """Called when the screen is left, useful for unbinding events."""
        Window.unbind(on_keyboard=self.on_key_pressed)
