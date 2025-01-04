# geostor/geostor/ui/project_ui.py
import sys
import os
import sqlite3

from PySide6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidget, 
    QVBoxLayout, 
    QFormLayout, 
    QLineEdit, 
    QPushButton, 
    QTableWidget, 
    QTableWidgetItem, 
    QMessageBox
)
from PySide6.QtCore import Qt

# Calculate the DB path relative to this file’s directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "..", "database", "geostor.db")
DB_PATH = os.path.normpath(DB_PATH)  # Optional: cleans up "../"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoStor Project Manager")

        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout()
        container.setLayout(main_layout)

        # 1. Project Table
        self.project_table = QTableWidget()
        self.project_table.setColumnCount(8)  # project_ID + 7 other fields
        self.project_table.setHorizontalHeaderLabels([
            "Project Number",
            "Project Name",
            "Location",
            "Client",
            "Contractor",
            "Engineer",
            "Comments",
            "File Ref"
        ])
        self.project_table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.project_table)

        # 2. Form to add new project
        form_layout = QFormLayout()
        self.project_number_input = QLineEdit()
        self.project_name_input = QLineEdit()
        self.project_location_input = QLineEdit()
        self.project_client_input = QLineEdit()
        self.project_contractor_input = QLineEdit()
        self.project_engineer_input = QLineEdit()
        self.project_comments_input = QLineEdit()
        self.file_reference_input = QLineEdit()

        form_layout.addRow("Project Number:", self.project_number_input)
        form_layout.addRow("Project Name:", self.project_name_input)
        form_layout.addRow("Location:", self.project_location_input)
        form_layout.addRow("Client:", self.project_client_input)
        form_layout.addRow("Contractor:", self.project_contractor_input)
        form_layout.addRow("Engineer:", self.project_engineer_input)
        form_layout.addRow("Comments:", self.project_comments_input)
        form_layout.addRow("File Ref:", self.file_reference_input)
        main_layout.addLayout(form_layout)

        # 3. Buttons
        self.add_button = QPushButton("Add Project")
        self.add_button.clicked.connect(self.add_project)
        main_layout.addWidget(self.add_button)

        self.refresh_button = QPushButton("Refresh Table")
        self.refresh_button.clicked.connect(self.load_projects)
        main_layout.addWidget(self.refresh_button)

        # 4. Load projects at startup
        self.load_projects()

    def load_projects(self):
        """
        Fetch existing projects from the SQLite DB and display in the table.
        """
        connection = None
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            cursor.execute("SELECT project_number, project_name, project_location, project_client, project_contractor, project_engineer, project_comments, file_reference FROM project")
            rows = cursor.fetchall()

            # Clear out existing rows
            self.project_table.setRowCount(0)

            for row_index, row_data in enumerate(rows):
                self.project_table.insertRow(row_index)
                for col_index, value in enumerate(row_data):
                    self.project_table.setItem(
                        row_index,
                        col_index,
                        QTableWidgetItem(str(value) if value else "")
                    )

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading projects:\n{e}")
        finally:
            if connection:
                connection.close()

    def add_project(self):
        """
        Add a new project record to the DB, then refresh the table.
        """
        project_number = self.project_number_input.text().strip()
        project_name = self.project_name_input.text().strip()
        project_location = self.project_location_input.text().strip()
        project_client = self.project_client_input.text().strip()
        project_contractor = self.project_contractor_input.text().strip()
        project_engineer = self.project_engineer_input.text().strip()
        project_comments = self.project_comments_input.text().strip()
        file_reference = self.file_reference_input.text().strip()

        # Validation
        if not project_number:
            QMessageBox.warning(self, "Validation Error", "Project Number is required.")
            return

        connection = None
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            insert_query = """
                INSERT INTO project (
                    project_number,
                    project_name,
                    project_location,
                    project_client,
                    project_contractor,
                    project_engineer,
                    project_comments,
                    file_reference
                ) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                project_number,
                project_name,
                project_location,
                project_client,
                project_contractor,
                project_engineer,
                project_comments,
                file_reference
            ))
            connection.commit()

            # Clear the fields
            self.project_number_input.clear()
            self.project_name_input.clear()
            self.project_location_input.clear()
            self.project_client_input.clear()
            self.project_contractor_input.clear()
            self.project_engineer_input.clear()
            self.project_comments_input.clear()
            self.file_reference_input.clear()

            QMessageBox.information(self, "Success", "Project added successfully.")
            self.load_projects()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error adding project:\n{e}")
        finally:
            if connection:
                connection.close()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
