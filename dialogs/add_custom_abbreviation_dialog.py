# geostor/geostor/dialogs/add_custom_abbreviation_dialog.py
import sqlite3
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "..", "database", "geostor.db")
DB_PATH = os.path.normpath(DB_PATH)


class AddCustomAbbreviationDialog(QDialog):
    """
    A reusable dialog for adding a custom abbreviation to the 'ags_abbreviations' table.
    You can specify the abbr_heading (e.g. 'LOCA_TYPE', 'LOCA_STAT') and dialog title.
    """
    def __init__(self, abbr_heading, dialog_title, parent=None):
        super().__init__(parent)
        self.abbr_heading = abbr_heading
        self.setWindowTitle(dialog_title)

        layout = QFormLayout()
        self.code_input = QLineEdit()
        self.desc_input = QLineEdit()
        layout.addRow("Code:", self.code_input)
        layout.addRow("Description:", self.desc_input)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.save_button.clicked.connect(self.handle_save)
        self.cancel_button.clicked.connect(self.reject)

    def handle_save(self):
        code = self.code_input.text().strip()
        desc = self.desc_input.text().strip()

        if not code:
            QMessageBox.warning(self, "Validation Error", "Code is required.")
            return

        # Insert the new record into 'ags_abbreviations'
        # Use abbr_list='custom' to denote user-defined abbreviations
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            insert_query = """
                INSERT INTO ags_abbreviations (
                    abbr_heading, abbr_code, abbr_description, abbr_list
                )
                VALUES (?, ?, ?, 'custom')
            """
            cursor.execute(insert_query, (self.abbr_heading, code, desc))
            connection.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error adding abbreviation:\n{e}")
            return
        finally:
            if connection:
                connection.close()

        QMessageBox.information(self, "Success", "Custom abbreviation added.")
        self.accept()
