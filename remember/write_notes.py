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
    def __init__(self, **kwargs):
        self.db = None
        self.cursor = None

        super().__init__(**kwargs)

        self.theme_cls.theme_style = "Light"

        if platform == "android":
            from android.storage import app_storage_path

            self.db_path = os.path.join(app_storage_path(), "notes.db")
        else:
            self.db_path = "./notes.db"

        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS labels
                                (id INTEGER PRIMARY KEY, label TEXT)"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS notes
                              (id INTEGER PRIMARY KEY, title TEXT, content TEXT, label TEXT REFERENCES labels(label))"""
        )
        self.db.commit()

        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        self.selected_label = None

        self.writenotes_title_label = MDLabel(
            text="[b]How was your last Conversation?[/b] [i]Write Here ...[/i]",
            markup=True,
            font_style="H4",
            halign="left",
        )

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

        existing_labels = self.get_predefined_labels()

        dropdown_menu = [
            {
                "viewclass": "OneLineListItem",
                "text": label,
                "on_release": lambda x=label: self.select_label(x),
            }
            for label in existing_labels
        ]

        self.menu = MDDropdownMenu(
            items=dropdown_menu,
            width_mult=4,
        )

        self.label_button = MDFillRoundFlatButton(
            text="[i]Label[/i]",
            size_hint_y=None,
            height=50,
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            theme_text_color="Custom",
            md_bg_color=self.theme_cls.primary_color,
            on_release=self.open_menu,  # Pass reference, not the function call
        )

        self.save_button = MDFillRoundFlatButton(
            text="Save Note",
            size_hint_y=None,
            height=50,
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            md_bg_color=self.theme_cls.primary_color,
            text_color=self.theme_cls.accent_color,
        )
        self.save_button.bind(on_press=self.save_note)

        layout.add_widget(self.writenotes_title_label)
        layout.add_widget(self.title_input)
        layout.add_widget(self.content_input)
        layout.add_widget(self.save_button)
        layout.add_widget(self.label_button)

        self.add_widget(layout)

        self.content_display = BoxLayout(
            orientation="vertical", padding=10, spacing=10, size_hint_y=None
        )
        self.scroll_view = ScrollView(size_hint=(1, None), size=(self.width, 300))
        self.scroll_view.add_widget(self.content_display)

        layout.add_widget(self.scroll_view)

    def get_predefined_labels(self):
        try:
            if (self.db is not None) and (self.cursor is not None):
                result = self.cursor.execute("""SELECT label FROM labels""")
                labels = [element[0] for element in result]
                labels.extend(["Work", "Personal", "Friend", "Other", "Add New Label"])
                labels = list(set(labels))
            else:
                self.db = sqlite3.connect(self.db_path)
                self.cursor = self.db.cursor()
                result = self.cursor.execute("""SELECT label FROM labels""")
                labels = [element[0] for element in result]
                labels.extend(["Work", "Personal", "Friend", "Other", "Add New Label"])
                labels = list(set(labels))
            return labels
        except sqlite3.Error as E:
            pass

    def select_label(self, label):
        self.selected_label = label

        if str(self.selected_label) == "Add New Label":
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
            save_label_button = MDRaisedButton(
                text="Save", on_release=self.save_new_label
            )

            # Add a widget to create space between the text field and button
            spacing_widget = Widget(
                size_hint_y=None, height=20
            )  # Adjust the height as needed

            layout = BoxLayout(orientation="vertical", padding=10)
            layout.add_widget(self.new_label_added)
            layout.add_widget(spacing_widget)  # Add the spacing widget here
            layout.add_widget(save_label_button)

            self.popup = Popup(
                title="Add New Label",
                content=layout,
                size_hint=(None, None),
                size=(400, 300),
            )
            self.popup.open()

            if not (self.selected_label == "Add New Label"):
                self.label_button.text = (
                    f"[i]{label}[/i]"  # Update button text to show the selected label
                )

            self.label_button.md_bg_color = (204 / 255, 119 / 255, 34 / 255, 1)
            self.menu.dismiss()

    def save_new_label(self, instance):
        self.selected_label = self.new_label_added.text
        self.label_button.text = f"[i]{self.selected_label}[/i]"

        self.menu.items.append(
            {
                "viewclass": "OneLineListItem",
                "text": self.selected_label,
                "on_release": lambda x=self.selected_label: self.select_label(x),
            }
        )

        new_label = self.new_label_added.text
        if new_label:
            try:
                self.cursor.execute(
                    "INSERT INTO labels (label) VALUES (?)", (new_label,)
                )
                self.db.commit()
                self.popup.dismiss()
                self.show_popup(f"New label '{new_label}' added successfully!")
            except sqlite3.Error as e:
                self.show_popup(f"Database error: {e}")

    def open_menu(self, button):
        """Open the dropdown menu when the button is clicked."""
        self.menu.caller = button  # Set the caller to the button that was clicked
        self.menu.open()

    def save_note(self, instance):
        title = self.title_input.text
        content = self.content_input.text

        # Check if a label is selected
        if not self.selected_label or self.selected_label == "Add New Label":
            self.show_popup("Please select a label before saving.")
            return

        if title and content:
            try:
                self.cursor.execute(
                    "INSERT INTO notes (title, content, label) VALUES (?, ?, ?)",
                    (title, content, self.selected_label),
                )
                self.db.commit()

                # Call the refresh function after saving the note
                self.refresh_ui()

                self.show_popup("Note saved successfully!")
            except sqlite3.Error as e:
                self.show_popup(f"Database error: {e}")
        else:
            self.show_popup("Please fill in Title & Conversations.")

    def refresh_ui(self):
        self.title_input.text = ""
        self.content_input.text = ""

        self.selected_label = None
        self.label_button.text = "[i]Label[/i]"
        self.label_button.md_bg_color = self.theme_cls.primary_color

        existing_labels = self.get_predefined_labels()

        dropdown_menu = [
            {
                "viewclass": "OneLineListItem",
                "text": label,
                "on_release": lambda x=label: self.select_label(x),
            }
            for label in existing_labels
        ]

        self.menu.items = dropdown_menu

        # # 4. (Optional) Refresh other UI elements, like a notes display area, if you have one
        # self.content_display.clear_widgets()  # If you display notes in a widget, clear it
        # self.load_notes()  # Load the notes again (implement this method if needed)

    def show_popup(self, message):
        dialog = MDDialog(
            text=message,
            buttons=[
                MDFillRoundFlatButton(text="OK", on_release=lambda x: dialog.dismiss()),
            ],
        )
        dialog.open()
