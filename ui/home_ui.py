import sys
import os
import sqlite3

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QLabel,
    QFrame
)
from PySide6.QtCore import Qt

from geostor.ui.location_ui import LocationWindow
from geostor.ui.project_ui import MainWindow

# Calculate the DB path relative to this file's directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "..", "database", "geostor.db")
DB_PATH = os.path.normpath(DB_PATH)

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoStor")
        self.setMinimumWidth(400)
        
        # Create main container and layout
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout()
        container.setLayout(main_layout)

        # Add title
        title_label = QLabel("GeoStor")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Add separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Project-specific section
        project_section = QWidget()
        project_layout = QVBoxLayout()
        project_section.setLayout(project_layout)

        # Project selection combo
        project_label = QLabel("Work with Project-Specific Data")
        project_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        project_layout.addWidget(project_label)

        combo_layout = QHBoxLayout()
        self.project_combo = QComboBox()
        self.load_projects()
        open_project_btn = QPushButton("Open Project")
        open_project_btn.clicked.connect(self.open_project_specific)
        
        combo_layout.addWidget(self.project_combo)
        combo_layout.addWidget(open_project_btn)
        project_layout.addLayout(combo_layout)

        main_layout.addWidget(project_section)

        # Add separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line2)

        # All data section
        all_data_section = QWidget()
        all_data_layout = QVBoxLayout()
        all_data_section.setLayout(all_data_layout)

        all_data_label = QLabel("Work with All Data")
        all_data_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        all_data_layout.addWidget(all_data_label)

        open_all_btn = QPushButton("Open Project Manager")
        open_all_btn.clicked.connect(self.open_all_data)
        all_data_layout.addWidget(open_all_btn)

        main_layout.addWidget(all_data_section)

        # Add stretcher to push everything up
        main_layout.addStretch()

    def load_projects(self):
        """Load projects into the combo box"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get all projects
            cursor.execute("SELECT project_id, project_number, project_name FROM project ORDER BY project_number")
            projects = cursor.fetchall()
            
            # Clear and populate combo box
            self.project_combo.clear()
            for project_id, project_number, project_name in projects:
                display_text = f"{project_number} - {project_name}" if project_name else project_number
                self.project_combo.addItem(display_text, project_id)
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            if conn:
                conn.close()

    def open_project_specific(self):
        """Open the location window with the selected project"""
        if self.project_combo.currentData():
            self.location_window = LocationWindow()
            
            # First load all projects in the location window
            self.location_window.load_projects()
            
            # Find the index of our selected project in the location window's combo
            project_id = self.project_combo.currentData()
            for i in range(self.location_window.project_combo.count()):
                if self.location_window.project_combo.itemData(i) == project_id:
                    self.location_window.project_combo.setCurrentIndex(i)
                    break
            
            self.location_window.show()

    def open_all_data(self):
        """Open the project manager window"""
        self.project_window = MainWindow()
        self.project_window.show()


def main():
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
