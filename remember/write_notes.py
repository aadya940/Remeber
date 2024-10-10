from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatButton, MDRaisedButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu

from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.uix.popup import Popup

import sqlite3
import os


class WriteNotesScreen(MDScreen):
    def __init__(self, _type=None, contact=None, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = "Light"
        self.selected_label = None
        self.contact = contact
        self._type = _type

        # Initialize the database
        self.setup_database()

        # Create the layout
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)
        self.create_ui_elements(layout)
        self.add_widget(layout)

        # Add scroll view for content display
        self.content_display = BoxLayout(
            orientation="vertical", padding=10, spacing=10, size_hint_y=None
        )
        self.scroll_view = ScrollView(size_hint=(1, None), size=(self.width, 300))
        self.scroll_view.add_widget(self.content_display)
        layout.add_widget(self.scroll_view)

        if self.contact is not None:
            self.prefill_contact_info()

    def prefill_contact_info(self):
        """Pre-fill the contact information into the input fields."""
        self.title_input.text = self.contact.get("name", "")
        self.content_input.text = self.contact.get("notes", "")
        self.label_button.text = self.contact.get("label", "")

    def setup_database(self):
        """Setup the SQLite database for storing notes and labels."""
        if self._type is not None:
            if self._type == "event":
                if platform == "android":
                    from android.storage import app_storage_path

                    self.db_path = os.path.join(app_storage_path(), "events.db")
                else:
                    self.db_path = "events.db"

                self.db = sqlite3.connect(self.db_path)
                self.cursor = self.db.cursor()

                self.cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS labels (
                        id INTEGER PRIMARY KEY, 
                        label TEXT)
                """
                )
                self.cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY, 
                        title TEXT, 
                        content TEXT, 
                        label TEXT REFERENCES labels(label))
                    """
                )
                self.db.commit()

                return
            else:
                raise ValueError(f"Unknown type recieved, found {self._type}")

        if platform == "android":
            from android.storage import app_storage_path

            self.db_path = os.path.join(app_storage_path(), "notes.db")
        else:
            self.db_path = "notes.db"

        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS labels (
                id INTEGER PRIMARY KEY, 
                label TEXT)
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY, 
                title TEXT, 
                content TEXT, 
                label TEXT REFERENCES labels(label))
        """
        )
        self.db.commit()

    def create_ui_elements(self, layout):
        """Create the main UI elements for writing and saving notes."""
        # Title Label
        self.writenotes_title_label = MDLabel(
            text="[b]How was your last Conversation?[/b] [i]Write Here ...[/i]",
            markup=True,
            font_style="H4",
            halign="left",
        )

        # Input Fields
        self.title_input = MDTextField(
            hint_text="Name",
            size_hint_y=None,
            height=50,
            mode="rectangle",
            radius=[10, 10, 10, 10],
            line_color_normal=self.theme_cls.primary_color,
            line_color_focus=self.theme_cls.accent_color,
            font_size="18sp",
            required=True,
        )

        self.content_input = MDTextField(
            hint_text="What did you talk about ...",
            multiline=True,
            size_hint_y=None,
            height=600,
            mode="rectangle",
            radius=[10, 10, 10, 10],
            line_color_normal=self.theme_cls.primary_color,
            line_color_focus=self.theme_cls.accent_color,
            font_size="16sp",
            required=True,
        )

        # Dropdown for Labels
        existing_labels = self.get_predefined_labels()
        dropdown_menu = [
            {
                "viewclass": "OneLineListItem",
                "text": label,
                "on_release": lambda x=label: self.select_label(x),
            }
            for label in existing_labels
        ]
        self.menu = MDDropdownMenu(items=dropdown_menu, width_mult=4)

        # Label Button
        self.label_button = MDFillRoundFlatButton(
            text="[i]Label[/i]",
            size_hint_y=None,
            height=50,
            pos_hint={"center_x": 0.5},
            theme_text_color="Custom",
            md_bg_color=self.theme_cls.primary_color,
            on_release=self.open_menu,
        )

        # Save Button
        self.save_button = MDFillRoundFlatButton(
            text="Save Note",
            size_hint_y=None,
            height=50,
            pos_hint={"center_x": 0.5},
            md_bg_color=self.theme_cls.primary_color,
            text_color=self.theme_cls.accent_color,
        )
        self.save_button.bind(on_press=self.save_note)

        if self._type == "event":
            self.writenotes_title_label.text = (
                "[b]How was your last Meeting?[/b] [i]Write Here ...[/i]"
            )
            self.title_input.hint_text = "Meeting title"
            self.content_input.hint_text = "What did you discuss in the meeting ..."

        # Add widgets to layout
        layout.add_widget(self.writenotes_title_label)
        layout.add_widget(self.title_input)
        layout.add_widget(self.content_input)
        layout.add_widget(self.label_button)
        layout.add_widget(self.save_button)

    def get_predefined_labels(self):
        """Retrieve labels from the database and add predefined ones."""
        if self._type == "event":
            result = self.cursor.execute("SELECT label FROM labels")
            labels = [element[0] for element in result] + ["Add New Label"]
            return list(set(labels))

        try:
            result = self.cursor.execute("SELECT label FROM labels")
            labels = [element[0] for element in result] + [
                "Work",
                "Personal",
                "Friend",
                "Other",
                "Add New Label",
            ]
            return list(set(labels))
        except sqlite3.Error:
            return ["Work", "Personal", "Friend", "Other", "Add New Label"]

    def select_label(self, label):
        """Handle label selection from the dropdown menu."""
        self.selected_label = label

        if label == "Add New Label":
            self.show_add_label_popup()

        else:
            self.label_button.text = f"[i]{label}[/i]"
            self.label_button.md_bg_color = (204 / 255, 119 / 255, 34 / 255, 1)

        self.menu.dismiss()

    def show_add_label_popup(self):
        """Show a popup for adding a new label."""
        self.new_label_added = MDTextField(
            hint_text="Your New Label ...",
            multiline=False,
            size_hint_y=None,
            height=200,
            padding=50,
            mode="rectangle",
            radius=[10, 10, 10, 10],
            line_color_normal=self.theme_cls.primary_color,
            line_color_focus=self.theme_cls.accent_color,
            font_size="18sp",
            required=True,
        )

        save_label_button = MDRaisedButton(text="Save", on_release=self.save_new_label)

        layout = BoxLayout(orientation="vertical", padding=10)
        layout.add_widget(self.new_label_added)
        layout.add_widget(Widget(size_hint_y=None, height=20))  # Spacing
        layout.add_widget(save_label_button)

        self.popup = Popup(
            title="Add New Label",
            content=layout,
            size_hint=(None, None),
            size=(400, 300),
        )
        self.popup.open()

    def save_new_label(self, instance):
        """Save the new label to the database."""
        new_label = self.new_label_added.text
        if new_label:
            try:
                self.cursor.execute(
                    "INSERT INTO labels (label) VALUES (?)", (new_label,)
                )
                self.db.commit()
                self.popup.dismiss()
                self.show_popup(f"New label '{new_label}' added successfully!")
                self.refresh_labels()
            except sqlite3.Error as e:
                self.show_popup(f"Database error: {e}")

    def open_menu(self, button):
        """Open the dropdown menu."""
        self.menu.caller = button
        self.menu.open()

    def save_note(self, instance):
        """Save the note to the database."""
        title = self.title_input.text
        content = self.content_input.text

        if not self.selected_label or self.selected_label == "Add New Label":
            self.show_popup("Please select a label before saving.")
            return

        if title and content:
            try:
                if self._type == "event":
                    self.cursor.execute(
                        "INSERT INTO labels (title, content, label) VALUES (?, ?, ?)",
                        (title, content, self.selected_label),
                    )
                else:
                    self.cursor.execute(
                        "INSERT INTO notes (title, content, label) VALUES (?, ?, ?)",
                        (title, content, self.selected_label),
                    )

                self.db.commit()
                self.refresh_ui()
                self.show_popup("Note saved successfully!")
            except sqlite3.Error as e:
                self.show_popup(f"Database error: {e}")
        else:
            self.show_popup("Please fill in Title & Conversations.")

    def refresh_labels(self):
        existing_labels = self.get_predefined_labels()
        self.menu.items = [
            {
                "viewclass": "OneLineListItem",
                "text": label,
                "on_release": lambda x=label: self.select_label(x),
            }
            for label in existing_labels
        ]

    def refresh_ui(self):
        """Clear the inputs and refresh the UI after saving a note."""
        self.title_input.text = ""
        self.content_input.text = ""
        self.selected_label = None
        self.label_button.text = "[i]Label[/i]"
        self.label_button.md_bg_color = self.theme_cls.primary_color

        self.refresh_labels()

    def show_popup(self, message):
        """Show a popup with a custom message."""
        dialog = MDDialog(
            text=message,
            buttons=[
                MDFillRoundFlatButton(text="OK", on_release=lambda x: dialog.dismiss())
            ],
        )
        dialog.open()
