from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog,
    QWidget
)
from PySide6.QtCore import Qt
import os
from pathlib import Path

from src.database.init_db import initialize_database

class DatabaseWizard(QWizard):
    def __init__(self, wizard_type="new"):
        super().__init__()
        
        self.wizard_type = wizard_type
        self.db_path = None
        
        self.setWindowTitle("Database Wizard")
        self.setWizardStyle(QWizard.ModernStyle)
        
        if wizard_type == "new":
            self.addPage(NewDatabasePage())
        else:
            self.addPage(ExistingDatabasePage())

class NewDatabasePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Create New Database")
        self.setSubTitle("Choose a location and name for the new database")
        
        layout = QVBoxLayout()
        
        # Database name input
        name_widget = QWidget()
        name_layout = QHBoxLayout(name_widget)
        name_layout.setContentsMargins(0, 0, 0, 0)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter database name")
        
        name_layout.addWidget(QLabel("Name:"))
        name_layout.addWidget(self.name_input)
        
        # Location selection
        location_widget = QWidget()
        location_layout = QHBoxLayout(location_widget)
        location_layout.setContentsMargins(0, 0, 0, 0)
        
        self.location_input = QLineEdit()
        self.location_input.setReadOnly(True)
        self.location_input.setPlaceholderText("Select location for database")
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_location)
        
        location_layout.addWidget(QLabel("Location:"))
        location_layout.addWidget(self.location_input)
        location_layout.addWidget(browse_button)
        
        # Add widgets to layout
        layout.addWidget(name_widget)
        layout.addWidget(location_widget)
        self.setLayout(layout)
        
        # Register fields
        self.registerField("new_db_name*", self.name_input)
        self.registerField("new_db_location*", self.location_input)
    
    def browse_location(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if directory:
            self.location_input.setText(directory)
    
    def validatePage(self):
        db_name = self.field("new_db_name")
        db_location = self.field("new_db_location")
        
        if not db_name:
            QMessageBox.warning(self, "Validation Error", "Please enter a database name.")
            return False
        
        if not db_location:
            QMessageBox.warning(self, "Validation Error", "Please select a location for the database.")
            return False
        
        # Create the database path
        db_path = Path(db_location) / f"{db_name}.db"
        
        # Check if database already exists
        if db_path.exists():
            QMessageBox.warning(
                self,
                "Database Exists",
                f"A database named '{db_name}' already exists in this location."
            )
            return False
        
        # Get the path to the AGS CSV file
        # First try to find it relative to the current file
        ags_csv_path = Path(__file__).parent.parent.parent / "database" / "AGS_abbreviations.csv"
        
        # If not found, try to find it relative to the project root
        if not ags_csv_path.exists():
            ags_csv_path = Path(__file__).parent.parent.parent.parent / "src" / "database" / "AGS_abbreviations.csv"
        
        if not ags_csv_path.exists():
            QMessageBox.warning(
                self,
                "Missing AGS CSV",
                "Could not find the AGS abbreviations file. Reference data will not be populated."
            )
            ags_csv_path = None
        
        # Initialize the database
        success, message = initialize_database(db_path, ags_csv_path=ags_csv_path)
        
        if not success:
            QMessageBox.critical(self, "Database Creation Error", message)
            return False
        
        self.wizard().db_path = str(db_path)
        return True

class ExistingDatabasePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Connect to Existing Database")
        self.setSubTitle("Select an existing database file")
        
        layout = QVBoxLayout()
        
        # Database file selection
        file_widget = QWidget()
        file_layout = QHBoxLayout(file_widget)
        file_layout.setContentsMargins(0, 0, 0, 0)
        
        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        self.file_input.setPlaceholderText("Select database file")
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_file)
        
        file_layout.addWidget(QLabel("Database:"))
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(browse_button)
        
        layout.addWidget(file_widget)
        self.setLayout(layout)
        
        # Register fields
        self.registerField("existing_db_path*", self.file_input)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Database File",
            "",
            "SQLite Database (*.db);;All Files (*.*)"
        )
        if file_path:
            self.file_input.setText(file_path)
    
    def validatePage(self):
        db_path = self.field("existing_db_path")
        
        if not db_path:
            QMessageBox.warning(self, "Validation Error", "Please select a database file.")
            return False
        
        if not os.path.exists(db_path):
            QMessageBox.warning(self, "File Not Found", "The selected database file does not exist.")
            return False
        
        self.wizard().db_path = db_path
        return True
