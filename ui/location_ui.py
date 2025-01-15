import sys
import os
import sqlite3

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QLabel,
    QDialog
)
from PySide6.QtCore import Qt

from geostor.dialogs.add_custom_abbreviation_dialog import AddCustomAbbreviationDialog


# Calculate the DB path relative to this file’s directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "..", "database", "geostor.db")
DB_PATH = os.path.normpath(DB_PATH)


class LocationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoStor Locations")

        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout()
        container.setLayout(main_layout)

        #
        # 1. Project Selection Combo
        #
        project_selection_layout = QHBoxLayout()
        project_label = QLabel("Select Project:")
        self.project_combo = QComboBox()
        self.project_combo.currentIndexChanged.connect(self.on_project_selected)

        project_selection_layout.addWidget(project_label)
        project_selection_layout.addWidget(self.project_combo)
        main_layout.addLayout(project_selection_layout)

        #
        # 2. Location Table (no location_id display)
        #
        # We will display many columns (minus location_id):
        self.location_table = QTableWidget()
        # Adjust column count & headers based on the fields you want to show
        self.location_table.setColumnCount(15)
        self.location_table.setHorizontalHeaderLabels([
            "Name",
            "Type",
            "Status",
            "Remarks",
            "Start Date",
            "End Date",
            "Latitude",
            "Longitude",
            "Easting",
            "Northing",
            "EPSG Code",
            "Ground Elevation",
            "Final Depth",
            "Original Job Ref",
            "Originating Company"
        ])
        self.location_table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.location_table)

        #
        # 3. Form to add or edit a location (minus location_id)
        #
        form_layout = QFormLayout()
        self.location_name_input = QLineEdit()

        # Location Type combo
        self.location_type_combo = QComboBox()

        # Location Status combo (new requirement)
        self.location_status_combo = QComboBox()

        self.location_remarks_input = QLineEdit()
        self.location_start_date_input = QLineEdit()
        self.location_end_date_input = QLineEdit()
        self.location_lat_input = QLineEdit()
        self.location_lon_input = QLineEdit()
        self.location_easting_input = QLineEdit()
        self.location_northing_input = QLineEdit()
        self.location_epsg_code_input = QLineEdit()
        self.location_ground_elevation_input = QLineEdit()
        self.location_final_depth_input = QLineEdit()
        self.location_original_job_ref_input = QLineEdit()
        self.location_originating_company_input = QLineEdit()

        type_layout = QHBoxLayout()
        type_layout.addWidget(self.location_type_combo)
        self.add_location_type_button = QPushButton("Add Custom Type")
        type_layout.addWidget(self.add_location_type_button)

        status_layout = QHBoxLayout()
        status_layout.addWidget(self.location_status_combo)
        self.add_location_status_button = QPushButton("Add Custom Status")
        status_layout.addWidget(self.add_location_status_button)        

        form_layout.addRow("Location Name:", self.location_name_input)
        # form_layout.addRow("Location Type:", self.location_type_combo)
        form_layout.addRow("Location Type:", type_layout)
        form_layout.addRow("Location Status:", status_layout)
        form_layout.addRow("Remarks:", self.location_remarks_input)
        form_layout.addRow("Start Date:", self.location_start_date_input)
        form_layout.addRow("End Date:", self.location_end_date_input)
        form_layout.addRow("Latitude:", self.location_lat_input)
        form_layout.addRow("Longitude:", self.location_lon_input)
        form_layout.addRow("Easting:", self.location_easting_input)
        form_layout.addRow("Northing:", self.location_northing_input)
        form_layout.addRow("EPSG Code:", self.location_epsg_code_input)
        form_layout.addRow("Ground Elevation:", self.location_ground_elevation_input)
        form_layout.addRow("Final Depth:", self.location_final_depth_input)
        form_layout.addRow("Original Job Ref:", self.location_original_job_ref_input)
        form_layout.addRow("Originating Company:", self.location_originating_company_input)

        main_layout.addLayout(form_layout)

        #
        # 4. Buttons
        #
        self.add_location_type_button.clicked.connect(self.on_add_custom_type_clicked)
        self.add_location_status_button.clicked.connect(self.on_add_custom_status_clicked)

        
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Location")
        self.add_button.clicked.connect(self.add_location)
        button_layout.addWidget(self.add_button)

        self.refresh_button = QPushButton("Refresh Table")
        self.refresh_button.clicked.connect(self.load_locations)
        button_layout.addWidget(self.refresh_button)
        main_layout.addLayout(button_layout)

        #
        # 5. Load Project combo data on startup
        #
        self.load_projects()

        #
        # 6. Load Location Type & Status combo data on startup
        #
        self.load_location_type_combo()
        self.load_location_status_combo()

    # -------------------------------------------------------------------------
    # DATABASE & COMBOBOX HELPERS
    # -------------------------------------------------------------------------

    def load_projects(self):
        """Fetch all projects from the DB and populate the combo box."""
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            cursor.execute("SELECT project_id, project_name FROM project")
            projects = cursor.fetchall()

            self.project_combo.clear()
            for project_id, project_name in projects:
                display_text = project_name if project_name else project_id
                self.project_combo.addItem(display_text, project_id)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading projects:\n{e}")
        finally:
            if connection:
                connection.close()

    def load_location_type_combo(self):
        """
        Fetch location types from the AGS abbreviations where abbr_heading='LOCA_TYPE'.
        """
        self.location_type_combo.clear()
        results = []
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            cursor.execute("""
                SELECT abbr_code, abbr_description 
                FROM ags_abbreviations
                WHERE abbr_heading = 'LOCA_TYPE'
            """)
            results = cursor.fetchall()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading location types:\n{e}")
        finally:
            if connection:
                connection.close()

        # Populate the combo box
        for abbr_code, abbr_description in results:
            text_to_show = abbr_description if abbr_description else abbr_code
            self.location_type_combo.addItem(text_to_show, abbr_code)

    def on_add_custom_type_clicked(self):
        dialog = AddCustomAbbreviationDialog(
            abbr_heading="LOCA_TYPE",
            dialog_title="Add Custom Location Type",
            parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            # The user successfully saved a new abbreviation
            self.load_location_type_combo()  # Refresh the combo

    def on_add_custom_status_clicked(self):
        dialog = AddCustomAbbreviationDialog(
            abbr_heading="LOCA_STAT",
            dialog_title="Add Custom Location Status",
            parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            self.load_location_status_combo()  # Refresh the combo

    def load_location_status_combo(self):
        """
        Fetch location status values from the AGS abbreviations where abbr_heading='LOCA_STAT'.
        """
        self.location_status_combo.clear()
        results = []
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            cursor.execute("""
                SELECT abbr_code, abbr_description 
                FROM ags_abbreviations
                WHERE abbr_heading = 'LOCA_STAT'
            """)
            results = cursor.fetchall()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading location status:\n{e}")
        finally:
            if connection:
                connection.close()

        # Populate the combo box
        for abbr_code, abbr_description in results:
            text_to_show = abbr_description if abbr_description else abbr_code
            self.location_status_combo.addItem(text_to_show, abbr_code)

    def get_current_project_id(self):
        """Returns the project_id associated with the current selection in the combo box."""
        index = self.project_combo.currentIndex()
        if index < 0:
            return None
        return self.project_combo.itemData(index)

    # -------------------------------------------------------------------------
    # LOAD & ADD LOCATIONS
    # -------------------------------------------------------------------------

    def on_project_selected(self, index):
        """Triggered when the user selects a different project in the combo box."""
        self.load_locations()

    def load_locations(self):
        """
        Fetch existing locations for the selected project
        and display in the table (excluding location_id).
        """
        project_id = self.get_current_project_id()
        if not project_id:
            return  # no valid project selected

        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Selecting all columns except location_id & project_id
            # We show them in the same order as the table column headers
            select_query = """
                SELECT 
                    location_name,
                    location_type,
                    location_status,
                    location_remarks,
                    location_start_date,
                    location_end_date,
                    location_lat,
                    location_lon,
                    location_easting,
                    location_northing,
                    location_epsg_code,
                    location_ground_elevation,
                    location_final_depth,
                    location_original_job_ref,
                    location_originating_company
                FROM location
                WHERE project_id = ?
                ORDER BY location_id
            """
            cursor.execute(select_query, (project_id,))
            rows = cursor.fetchall()

            self.location_table.setRowCount(0)
            for row_index, row_data in enumerate(rows):
                self.location_table.insertRow(row_index)
                for col_index, value in enumerate(row_data):
                    item_text = str(value) if value is not None else ""
                    self.location_table.setItem(row_index, col_index, QTableWidgetItem(item_text))

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading locations:\n{e}")
        finally:
            if connection:
                connection.close()

    def add_location(self):
        """
        Insert a new location record into the DB for the currently selected project.
        """
        project_id = self.get_current_project_id()
        if not project_id:
            QMessageBox.warning(self, "Validation Error", "No valid project selected.")
            return

        # Gather inputs
        location_name = self.location_name_input.text().strip()
        location_type = self.location_type_combo.currentData()  # store code from combo
        location_status = self.location_status_combo.currentData()  # store code from combo
        location_remarks = self.location_remarks_input.text().strip()
        location_start_date = self.location_start_date_input.text().strip()
        location_end_date = self.location_end_date_input.text().strip()
        location_lat = self.location_lat_input.text().strip()
        location_lon = self.location_lon_input.text().strip()
        location_easting = self.location_easting_input.text().strip()
        location_northing = self.location_northing_input.text().strip()
        location_epsg_code = self.location_epsg_code_input.text().strip()
        location_ground_elevation = self.location_ground_elevation_input.text().strip()
        location_final_depth = self.location_final_depth_input.text().strip()
        location_original_job_ref = self.location_original_job_ref_input.text().strip()
        location_originating_company = self.location_originating_company_input.text().strip()

        # Simple validation
        if not location_name:
            QMessageBox.warning(self, "Validation Error", "Location Name is required.")
            return

        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            insert_query = """
                INSERT INTO location (
                    project_id,
                    location_name,
                    location_type,
                    location_status,
                    location_remarks,
                    location_start_date,
                    location_end_date,
                    location_lat,
                    location_lon,
                    location_easting,
                    location_northing,
                    location_epsg_code,
                    location_ground_elevation,
                    location_final_depth,
                    location_original_job_ref,
                    location_originating_company
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                project_id,
                location_name,
                location_type,
                location_status,
                location_remarks,
                location_start_date,
                location_end_date,
                location_lat,
                location_lon,
                location_easting,
                location_northing,
                location_epsg_code,
                location_ground_elevation,
                location_final_depth,
                location_original_job_ref,
                location_originating_company
            ))
            connection.commit()

            # Clear input fields
            self.location_name_input.clear()
            self.location_type_combo.setCurrentIndex(-1)
            self.location_status_combo.setCurrentIndex(-1)
            self.location_remarks_input.clear()
            self.location_start_date_input.clear()
            self.location_end_date_input.clear()
            self.location_lat_input.clear()
            self.location_lon_input.clear()
            self.location_easting_input.clear()
            self.location_northing_input.clear()
            self.location_epsg_code_input.clear()
            self.location_ground_elevation_input.clear()
            self.location_final_depth_input.clear()
            self.location_original_job_ref_input.clear()
            self.location_originating_company_input.clear()

            QMessageBox.information(self, "Success", "Location added successfully.")
            self.load_locations()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error adding location:\n{e}")
        finally:
            if connection:
                connection.close()


def main():
    app = QApplication(sys.argv)
    window = LocationWindow()
    window.resize(1200, 700)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
