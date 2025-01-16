import sys
import os
import sqlite3

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QComboBox,
    QLabel,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QGroupBox,
    QFrame,
    QToolButton,
    QSplitter,
    QSizePolicy,
    QScrollArea,
    QDialog
)
from PySide6.QtCore import Qt

from geostor.dialogs.add_custom_abbreviation_dialog import AddCustomAbbreviationDialog

#
# 1. A helper 'CollapsibleFrame' for the Additional Information
#
class CollapsibleFrame(QFrame):
    """
    A collapsible frame that uses a QToolButton to show/hide content,
    and wraps the content in a scrollable area so any overflow is accessible.
    """
    def __init__(self, title="Additional Information", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # A toggle button at the top
        self.toggle_button = QToolButton()
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.clicked.connect(self.on_toggle)

        # Create a QScrollArea to hold the actual form/layout
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # An inner widget that goes inside the scroll area
        self.inner_widget = QWidget()
        self.content_layout = QVBoxLayout(self.inner_widget)
        self.inner_widget.setLayout(self.content_layout)

        # Put that inner widget into the scroll area
        self.scroll_area.setWidget(self.inner_widget)

        # Initially collapsed: hide the scroll area
        self.scroll_area.setMaximumHeight(0)

        # Build the frame layout
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.scroll_area)

    def on_toggle(self):
        """
        Expand or collapse the scrollable content.
        """
        if self.toggle_button.isChecked():
            self.toggle_button.setArrowType(Qt.ArrowType.DownArrow)
            self.scroll_area.setMaximumHeight(16777215)  # effectively no maximum
        else:
            self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
            self.scroll_area.setMaximumHeight(0)

    def addLayout(self, layout):
        """
        Add a layout (e.g., QFormLayout) to our scrollable inner widget.
        """
        self.content_layout.addLayout(layout)


#
# Path to the DB
#
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "..", "database", "geostor.db")
DB_PATH = os.path.normpath(DB_PATH)


class SampleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoStor - Samples")
        
        # Set window size for 1080p
        self.resize(1280, 800)  # More conservative size that should work on most displays
        
        # Main container with a horizontal layout
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QHBoxLayout()
        container.setLayout(main_layout)

        # Splitter for left (form) and right (table)
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)

        #
        # LEFT PANEL (30% - ~384px)
        #
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        self.splitter.addWidget(left_widget)
        left_widget.setMinimumWidth(350)
        left_widget.setMaximumWidth(400)

        #
        # 1a. Project & Location Selection at the top
        #
        selection_layout = QHBoxLayout()
        self.project_combo = QComboBox()
        self.location_combo = QComboBox()

        selection_layout.addWidget(QLabel("Project:"))
        selection_layout.addWidget(self.project_combo)
        selection_layout.addWidget(QLabel("Location:"))
        selection_layout.addWidget(self.location_combo)

        left_layout.addLayout(selection_layout)

        # Connect signals
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)
        self.location_combo.currentIndexChanged.connect(self.load_samples)

        #
        # 1b. Primary Information Group
        #
        primary_group = QGroupBox("Primary Information")
        primary_form = QFormLayout()

        # 8 fields for the Primary frame
        self.sample_reference_input = QLineEdit()

        sample_type_layout = QHBoxLayout()
        self.sample_type_combo = QComboBox()
        self.add_sample_type_button = QPushButton("Add Custom Type")
        sample_type_layout.addWidget(self.sample_type_combo)
        sample_type_layout.addWidget(self.add_sample_type_button)
        
        self.sample_top_depth_input = QLineEdit()
        self.sample_base_depth_input = QLineEdit()
        self.sample_description_input = QLineEdit()
        self.sample_stratum_reference_input = QLineEdit()
        self.sample_recovery_length_input = QLineEdit()
        self.sample_recovery_percent_input = QLineEdit()

        primary_form.addRow("Sample Ref:", self.sample_reference_input)
        primary_form.addRow("Sample Type:", sample_type_layout)
        primary_form.addRow("Top Depth:", self.sample_top_depth_input)
        primary_form.addRow("Base Depth:", self.sample_base_depth_input)
        primary_form.addRow("Description:", self.sample_description_input)
        primary_form.addRow("Stratum Ref:", self.sample_stratum_reference_input)
        primary_form.addRow("Recovery (Length):", self.sample_recovery_length_input)
        primary_form.addRow("Recovery (Percent):", self.sample_recovery_percent_input)

        # Connect signals
        self.add_sample_type_button.clicked.connect(self.on_add_custom_sample_type_clicked)

        self.load_sample_types()


        primary_group.setLayout(primary_form)
        left_layout.addWidget(primary_group)

        #
        # 1c. Additional Information (collapsible)
        #
        self.additional_frame = CollapsibleFrame("Additional Information")
        additional_form = QFormLayout()

        # All remaining fields go here
        self.sample_date_time_input = QLineEdit()
        self.sample_blows_input = QLineEdit()
        self.sample_container_input = QLineEdit()
        self.sample_preparation_input = QLineEdit()
        self.sample_diameter_input = QLineEdit()
        self.sample_water_depth_input = QLineEdit()
        self.sample_method_input = QLineEdit()
        self.sample_matrix_input = QLineEdit()
        self.sample_qa_type_input = QLineEdit()
        self.sample_collector_input = QLineEdit()
        self.sample_reason_input = QLineEdit()
        self.sample_remarks_input = QLineEdit()
        self.sample_description_date_input = QLineEdit()
        self.sample_logger_input = QLineEdit()
        self.sample_condition_input = QLineEdit()
        self.sample_classification_input = QLineEdit()
        self.sample_barometric_pressure_input = QLineEdit()
        self.sample_temperature_input = QLineEdit()
        self.sample_gas_pressure_input = QLineEdit()
        self.sample_gas_flow_rate_input = QLineEdit()
        self.sample_end_date_time_input = QLineEdit()
        self.sample_duration_input = QLineEdit()
        self.sample_caption_input = QLineEdit()
        self.sample_record_link_input = QLineEdit()
        self.file_reference_input = QLineEdit()

        # Add them all
        additional_form.addRow("Date/Time:", self.sample_date_time_input)
        additional_form.addRow("Blows (#):", self.sample_blows_input)
        additional_form.addRow("Container:", self.sample_container_input)
        additional_form.addRow("Preparation:", self.sample_preparation_input)
        additional_form.addRow("Diameter:", self.sample_diameter_input)
        additional_form.addRow("Water Depth:", self.sample_water_depth_input)
        additional_form.addRow("Method:", self.sample_method_input)
        additional_form.addRow("Matrix:", self.sample_matrix_input)
        additional_form.addRow("QA Type:", self.sample_qa_type_input)
        additional_form.addRow("Collector (Who):", self.sample_collector_input)
        additional_form.addRow("Reason (Why):", self.sample_reason_input)
        additional_form.addRow("Remarks:", self.sample_remarks_input)
        additional_form.addRow("Description Date:", self.sample_description_date_input)
        additional_form.addRow("Logger:", self.sample_logger_input)
        additional_form.addRow("Condition:", self.sample_condition_input)
        additional_form.addRow("Classification:", self.sample_classification_input)
        additional_form.addRow("Barometric Pressure:", self.sample_barometric_pressure_input)
        additional_form.addRow("Temperature:", self.sample_temperature_input)
        additional_form.addRow("Gas Pressure:", self.sample_gas_pressure_input)
        additional_form.addRow("Gas Flow Rate:", self.sample_gas_flow_rate_input)
        additional_form.addRow("End Date/Time:", self.sample_end_date_time_input)
        additional_form.addRow("Duration:", self.sample_duration_input)
        additional_form.addRow("Caption:", self.sample_caption_input)
        additional_form.addRow("Record Link:", self.sample_record_link_input)
        additional_form.addRow("File Reference:", self.file_reference_input)

        self.additional_frame.addLayout(additional_form)
        left_layout.addWidget(self.additional_frame)

        #
        # 1d. "Add Sample" button
        #
        save_button = QPushButton("Add Sample")
        save_button.clicked.connect(self.add_sample)
        left_layout.addWidget(save_button)
        left_layout.addStretch()

        #
        # RIGHT PANEL (70%)
        #
        self.table_widget = QTableWidget()
        # Let the table widget expand naturally without fixed width
        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # We'll have columns for all fields (33), skipping 'location_id' as it's a foreign key
        field_names = [
            "sample_top_depth",
            "sample_reference",
            "sample_type",
            "sample_base_depth",
            "sample_date_time",
            "sample_blows",
            "sample_container",
            "sample_preparation",
            "sample_diameter",
            "sample_water_depth",
            "sample_recovery_percent",
            "sample_method",
            "sample_matrix",
            "sample_qa_type",
            "sample_collector",
            "sample_reason",
            "sample_remarks",
            "sample_description",
            "sample_description_date",
            "sample_logger",
            "sample_condition",
            "sample_classification",
            "sample_barometric_pressure",
            "sample_temperature",
            "sample_gas_pressure",
            "sample_gas_flow_rate",
            "sample_end_date_time",
            "sample_duration",
            "sample_caption",
            "sample_record_link",
            "sample_stratum_reference",
            "file_reference",
            "sample_recovery_length"
        ]
        self.all_fields = field_names  # We'll use this for SELECT order
        self.table_widget.setColumnCount(len(field_names))
        self.table_widget.setHorizontalHeaderLabels(field_names)
        # Enable horizontal scrolling
        self.table_widget.horizontalHeader().setStretchLastSection(False)

        self.splitter.addWidget(self.table_widget)
        self.splitter.setStretchFactor(0, 3)  # left side 30%
        self.splitter.setStretchFactor(1, 7)  # right side 70%

        #
        # Initial Load
        #
        self.load_projects()

    # ---------------------------------------------------------------------
    # 1. Project & Location Loading
    # ---------------------------------------------------------------------
    def load_projects(self):
        self.project_combo.clear()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT project_id, project_name FROM project")
            rows = cursor.fetchall()
            for project_id, project_name in rows:
                display_text = project_name if project_name else project_id
                self.project_combo.addItem(display_text, project_id)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "DB Error", f"Error loading projects:\n{e}")
        finally:
            conn.close()

        # If there's at least one project, trigger location loading
        if self.project_combo.count() > 0:
            self.on_project_changed(0)

    def on_project_changed(self, index):
        project_id = self.get_current_project_id()
        if not project_id:
            return

        self.location_combo.clear()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT location_id, location_name 
                FROM location 
                WHERE project_id=?
            """, (project_id,))
            rows = cursor.fetchall()
            for loc_id, loc_name in rows:
                display_text = loc_name if loc_name else str(loc_id)
                self.location_combo.addItem(display_text, loc_id)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "DB Error", f"Error loading locations:\n{e}")
        finally:
            conn.close()

        if self.location_combo.count() > 0:
            self.load_samples()

    def get_current_project_id(self):
        idx = self.project_combo.currentIndex()
        if idx < 0:
            return None
        return self.project_combo.itemData(idx)

    def get_current_location_id(self):
        idx = self.location_combo.currentIndex()
        if idx < 0:
            return None
        return self.location_combo.itemData(idx)

    # ---------------------------------------------------------------------
    # 2. Load Samples (Table)
    # ---------------------------------------------------------------------
    def load_samples(self):
        location_id = self.get_current_location_id()
        if not location_id:
            return

        # Build a SELECT for all fields in self.all_fields
        # location_id is used in the WHERE but not selected
        select_query = f"""
            SELECT {', '.join(self.all_fields)} 
            FROM sample
            WHERE location_id=?
            ORDER BY sample_top_depth
        """

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(select_query, (location_id,))
            rows = cursor.fetchall()
            conn.close()

            self.table_widget.setRowCount(0)
            for row_index, row_data in enumerate(rows):
                self.table_widget.insertRow(row_index)
                for col_index, value in enumerate(row_data):
                    item_text = str(value) if value is not None else ""
                    self.table_widget.setItem(row_index, col_index, QTableWidgetItem(item_text))

        except sqlite3.Error as e:
            QMessageBox.critical(self, "DB Error", f"Error loading samples:\n{e}")

    # ---------------------------------------------------------------------
    # 3. Add Sample
    # ---------------------------------------------------------------------
    def add_sample(self):
        location_id = self.get_current_location_id()
        if not location_id:
            QMessageBox.warning(self, "Validation Error", "No valid location selected.")
            return

        # Primary fields
        top_depth = self.sample_top_depth_input.text().strip()
        sample_ref = self.sample_reference_input.text().strip()
        sample_type = self.sample_type_combo.currentData()
        base_depth = self.sample_base_depth_input.text().strip()
        description = self.sample_description_input.text().strip()
        stratum_ref = self.sample_stratum_reference_input.text().strip()
        recovery_len = self.sample_recovery_length_input.text().strip()
        recovery_pct = self.sample_recovery_percent_input.text().strip()

        if not top_depth or not sample_ref or not sample_type:
            QMessageBox.warning(
                self,
                "Validation Error",
                "sample_top_depth, sample_reference, and sample_type are required."
            )
            return

        # Additional fields
        date_time = self.sample_date_time_input.text().strip()
        blows = self.sample_blows_input.text().strip()
        container = self.sample_container_input.text().strip()
        preparation = self.sample_preparation_input.text().strip()
        diameter = self.sample_diameter_input.text().strip()
        water_depth = self.sample_water_depth_input.text().strip()
        method = self.sample_method_input.text().strip()
        matrix = self.sample_matrix_input.text().strip()
        qa_type = self.sample_qa_type_input.text().strip()
        collector = self.sample_collector_input.text().strip()
        reason = self.sample_reason_input.text().strip()
        remarks = self.sample_remarks_input.text().strip()
        description_date = self.sample_description_date_input.text().strip()
        logger = self.sample_logger_input.text().strip()
        condition = self.sample_condition_input.text().strip()
        classification = self.sample_classification_input.text().strip()
        bar_press = self.sample_barometric_pressure_input.text().strip()
        temperature = self.sample_temperature_input.text().strip()
        gas_press = self.sample_gas_pressure_input.text().strip()
        gas_flow = self.sample_gas_flow_rate_input.text().strip()
        end_datetime = self.sample_end_date_time_input.text().strip()
        duration = self.sample_duration_input.text().strip()
        caption = self.sample_caption_input.text().strip()
        record_link = self.sample_record_link_input.text().strip()
        file_ref = self.file_reference_input.text().strip()

        # Insert query must match all columns in the correct order
        insert_query = """
            INSERT INTO sample (
                location_id,
                sample_top_depth,
                sample_reference,
                sample_type,
                sample_base_depth,
                sample_date_time,
                sample_blows,
                sample_container,
                sample_preparation,
                sample_diameter,
                sample_water_depth,
                sample_recovery_percent,
                sample_method,
                sample_matrix,
                sample_qa_type,
                sample_collector,
                sample_reason,
                sample_remarks,
                sample_description,
                sample_description_date,
                sample_logger,
                sample_condition,
                sample_classification,
                sample_barometric_pressure,
                sample_temperature,
                sample_gas_pressure,
                sample_gas_flow_rate,
                sample_end_date_time,
                sample_duration,
                sample_caption,
                sample_record_link,
                sample_stratum_reference,
                file_reference,
                sample_recovery_length
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        # 33 placeholders total (location_id + 32 sample fields)
        values = (
            location_id,
            top_depth,
            sample_ref,
            sample_type,
            base_depth,
            date_time,
            blows,
            container,
            preparation,
            diameter,
            water_depth,
            recovery_pct,
            method,
            matrix,
            qa_type,
            collector,
            reason,
            remarks,
            description,
            description_date,
            logger,
            condition,
            classification,
            bar_press,
            temperature,
            gas_press,
            gas_flow,
            end_datetime,
            duration,
            caption,
            record_link,
            stratum_ref,
            file_ref,
            recovery_len
        )

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(insert_query, values)
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Sample added successfully.")
            self.clear_form_fields()
            self.load_samples()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "DB Error", f"Error adding sample:\n{e}")

    def load_sample_types(self):
        """
        Populate self.sample_type_combo from ags_abbreviations where abbr_heading='SAMP_TYPE'.
        """
        self.sample_type_combo.clear()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT abbr_code, abbr_description
                FROM ags_abbreviations
                WHERE abbr_heading = 'SAMP_TYPE'
                ORDER BY abbr_code
            """)
            rows = cursor.fetchall()
            conn.close()

            for abbr_code, abbr_desc in rows:
                display_text = abbr_desc if abbr_desc else abbr_code
                # Use abbr_code as the "data"; display desc or code
                self.sample_type_combo.addItem(display_text, abbr_code)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "DB Error", f"Error loading sample types:\n{e}")

    def on_add_custom_sample_type_clicked(self):
        dialog = AddCustomAbbreviationDialog(
            abbr_heading="SAMP_TYPE",
            dialog_title="Add Custom Sample Type",
            parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            self.load_sample_types()            
    
    
    def clear_form_fields(self):
        """
        Reset the form fields.
        """
        # Primary
        self.sample_top_depth_input.clear()
        self.sample_reference_input.clear()
        self.sample_type_combo.setCurrentIndex(0)
        self.sample_base_depth_input.clear()
        self.sample_description_input.clear()
        self.sample_stratum_reference_input.clear()
        self.sample_recovery_length_input.clear()
        self.sample_recovery_percent_input.clear()

        # Additional
        self.sample_date_time_input.clear()
        self.sample_blows_input.clear()
        self.sample_container_input.clear()
        self.sample_preparation_input.clear()
        self.sample_diameter_input.clear()
        self.sample_water_depth_input.clear()
        self.sample_method_input.clear()
        self.sample_matrix_input.clear()
        self.sample_qa_type_input.clear()
        self.sample_collector_input.clear()
        self.sample_reason_input.clear()
        self.sample_remarks_input.clear()
        self.sample_description_date_input.clear()
        self.sample_logger_input.clear()
        self.sample_condition_input.clear()
        self.sample_classification_input.clear()
        self.sample_barometric_pressure_input.clear()
        self.sample_temperature_input.clear()
        self.sample_gas_pressure_input.clear()
        self.sample_gas_flow_rate_input.clear()
        self.sample_end_date_time_input.clear()
        self.sample_duration_input.clear()
        self.sample_caption_input.clear()
        self.sample_record_link_input.clear()
        self.file_reference_input.clear()


def main():
    app = QApplication(sys.argv)
    window = SampleWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
