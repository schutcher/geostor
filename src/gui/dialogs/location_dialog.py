from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel,
    QComboBox, QMessageBox, QWidget, QFileDialog, QScrollArea
)
from PySide6.QtCore import Qt


class LocationDialog(QDialog):
    """Dialog for adding/editing locations"""
    
    def __init__(self, parent=None, location=None, db=None):
        super().__init__(parent)
        self.location = location
        self.db = db
        self.setup_ui()
        
        # If editing an existing location, populate the fields
        if location:
            self.name.setText(location.name)
            if location.type:
                index = self.type.findText(location.type)
                if index >= 0:
                    self.type.setCurrentIndex(index)
            if location.status:
                index = self.status.findText(location.status)
                if index >= 0:
                    self.status.setCurrentIndex(index)
            if location.lon is not None:
                self.longitude.setText(str(location.lon))
            if location.lat is not None:
                self.latitude.setText(str(location.lat))
            if location.ground_elevation is not None:
                self.elevation.setText(str(location.ground_elevation))
            if location.final_depth is not None:
                self.final_depth.setText(str(location.final_depth))
            if location.start_date:
                self.start_date.setText(location.start_date)
            if location.end_date:
                self.end_date.setText(location.end_date)
            if location.purpose:
                self.purpose.setText(location.purpose)
            if location.method:
                self.method.setText(location.method)
            if location.termination_reason:
                self.termination_reason.setText(location.termination_reason)
            if location.letter_grid_ref:
                self.letter_grid_ref.setText(location.letter_grid_ref)
            if location.local_x is not None:
                self.local_x.setText(str(location.local_x))
            if location.local_y is not None:
                self.local_y.setText(str(location.local_y))
            if location.local_z is not None:
                self.local_z.setText(str(location.local_z))
            if location.local_grid_ref_system:
                self.local_grid_ref_system.setText(location.local_grid_ref_system)
            if location.local_datum_system:
                self.local_datum_system.setText(location.local_datum_system)
            if location.easting_end_traverse is not None:
                self.easting_end_traverse.setText(str(location.easting_end_traverse))
            if location.northing_end_traverse is not None:
                self.northing_end_traverse.setText(str(location.northing_end_traverse))
            if location.ground_level_end_traverse is not None:
                self.ground_level_end_traverse.setText(str(location.ground_level_end_traverse))
            if location.local_x_end_traverse is not None:
                self.local_x_end_traverse.setText(str(location.local_x_end_traverse))
            if location.local_y_end_traverse is not None:
                self.local_y_end_traverse.setText(str(location.local_y_end_traverse))
            if location.local_z_end_traverse is not None:
                self.local_z_end_traverse.setText(str(location.local_z_end_traverse))
            if location.end_lat is not None:
                self.end_lat.setText(str(location.end_lat))
            if location.end_lon is not None:
                self.end_lon.setText(str(location.end_lon))
            if location.projection_format:
                self.projection_format.setText(location.projection_format)
            if location.sub_division:
                self.sub_division.setText(location.sub_division)
            if location.phase_grouping_code:
                self.phase_grouping_code.setText(location.phase_grouping_code)
            if location.alignment_id is not None:
                self.alignment_id.setText(str(location.alignment_id))
            if location.offset is not None:
                self.offset.setText(str(location.offset))
            if location.chainage is not None:
                self.chainage.setText(str(location.chainage))
            if location.algorithm_ref:
                self.algorithm_ref.setText(location.algorithm_ref)
            if location.file_reference:
                self.file_reference.setText(location.file_reference)
            if location.national_datum_system:
                self.national_datum_system.setText(location.national_datum_system)
            if location.original_hole_id:
                self.original_hole_id.setText(location.original_hole_id)
            if location.original_job_ref:
                self.original_job_ref.setText(location.original_job_ref)
            if location.originating_company:
                self.originating_company.setText(location.originating_company)
            if location.remarks:
                self.remarks.setText(location.remarks)
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Location Details")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Create scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setLayout(form_layout)
        scroll.setWidget(scroll_widget)
        
        # Create form fields
        self.name = QLineEdit(self)
        self.type = QComboBox(self)
        self.status = QComboBox(self)
        self.longitude = QLineEdit(self)
        self.latitude = QLineEdit(self)
        self.elevation = QLineEdit(self)
        self.final_depth = QLineEdit(self)
        self.start_date = QLineEdit(self)
        self.end_date = QLineEdit(self)
        self.purpose = QLineEdit(self)
        self.method = QLineEdit(self)
        self.termination_reason = QLineEdit(self)
        self.letter_grid_ref = QLineEdit(self)
        self.local_x = QLineEdit(self)
        self.local_y = QLineEdit(self)
        self.local_z = QLineEdit(self)
        self.local_grid_ref_system = QLineEdit(self)
        self.local_datum_system = QLineEdit(self)
        self.easting_end_traverse = QLineEdit(self)
        self.northing_end_traverse = QLineEdit(self)
        self.ground_level_end_traverse = QLineEdit(self)
        self.local_x_end_traverse = QLineEdit(self)
        self.local_y_end_traverse = QLineEdit(self)
        self.local_z_end_traverse = QLineEdit(self)
        self.end_lat = QLineEdit(self)
        self.end_lon = QLineEdit(self)
        self.projection_format = QLineEdit(self)
        self.sub_division = QLineEdit(self)
        self.phase_grouping_code = QLineEdit(self)
        self.alignment_id = QLineEdit(self)
        self.offset = QLineEdit(self)
        self.chainage = QLineEdit(self)
        self.algorithm_ref = QLineEdit(self)
        self.file_reference = QLineEdit(self)
        self.national_datum_system = QLineEdit(self)
        self.original_hole_id = QLineEdit(self)
        self.original_job_ref = QLineEdit(self)
        self.originating_company = QLineEdit(self)
        self.remarks = QLineEdit(self)
        
        # Setup type dropdown
        if self.db:
            type_abbrs = self.db.get_ags_abbreviations("LOCA_TYPE")
            for abbr in type_abbrs:
                self.type.addItem(f"{abbr.abbr_code} - {abbr.abbr_description}", abbr.abbr_code)
        default_type = "EH - Exploratory Hole"
        index = self.type.findText(default_type)
        if index >= 0:
            self.type.setCurrentIndex(index)
        
        # Setup status dropdown
        if self.db:
            status_abbrs = self.db.get_ags_abbreviations("LOCA_STAT")
            for abbr in status_abbrs:
                self.status.addItem(f"{abbr.abbr_code} - {abbr.abbr_description}", abbr.abbr_code)
        default_status = "PROPOSED"
        index = self.status.findText(default_status, Qt.MatchContains)
        if index >= 0:
            self.status.setCurrentIndex(index)
        
        # Add fields to layout in specified order
        form_layout.addRow("Name:", self.name)
        form_layout.addRow("Type:", self.type)
        form_layout.addRow("Status:", self.status)
        form_layout.addRow("Longitude:", self.longitude)
        form_layout.addRow("Latitude:", self.latitude)
        form_layout.addRow("Ground Elevation:", self.elevation)
        form_layout.addRow("Final Depth:", self.final_depth)
        form_layout.addRow("Start Date:", self.start_date)
        form_layout.addRow("End Date:", self.end_date)
        form_layout.addRow("Purpose:", self.purpose)
        form_layout.addRow("Method:", self.method)
        form_layout.addRow("Termination Reason:", self.termination_reason)
        form_layout.addRow("Letter Grid Ref:", self.letter_grid_ref)
        form_layout.addRow("Local X:", self.local_x)
        form_layout.addRow("Local Y:", self.local_y)
        form_layout.addRow("Local Z:", self.local_z)
        form_layout.addRow("Local Grid System:", self.local_grid_ref_system)
        form_layout.addRow("Local Datum System:", self.local_datum_system)
        form_layout.addRow("Easting End Traverse:", self.easting_end_traverse)
        form_layout.addRow("Northing End Traverse:", self.northing_end_traverse)
        form_layout.addRow("Ground Level End Traverse:", self.ground_level_end_traverse)
        form_layout.addRow("Local X End Traverse:", self.local_x_end_traverse)
        form_layout.addRow("Local Y End Traverse:", self.local_y_end_traverse)
        form_layout.addRow("Local Z End Traverse:", self.local_z_end_traverse)
        form_layout.addRow("End Latitude:", self.end_lat)
        form_layout.addRow("End Longitude:", self.end_lon)
        form_layout.addRow("Projection Format:", self.projection_format)
        form_layout.addRow("Sub Division:", self.sub_division)
        form_layout.addRow("Phase/Grouping Code:", self.phase_grouping_code)
        form_layout.addRow("Alignment ID:", self.alignment_id)
        form_layout.addRow("Offset:", self.offset)
        form_layout.addRow("Chainage:", self.chainage)
        form_layout.addRow("Algorithm Reference:", self.algorithm_ref)
        form_layout.addRow("File Reference:", self.file_reference)
        form_layout.addRow("National Datum System:", self.national_datum_system)
        form_layout.addRow("Original Hole ID:", self.original_hole_id)
        form_layout.addRow("Original Job Reference:", self.original_job_ref)
        form_layout.addRow("Originating Company:", self.originating_company)
        form_layout.addRow("Remarks:", self.remarks)
        
        # Add buttons at the bottom
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save", self)
        cancel_button = QPushButton("Cancel", self)

        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addWidget(scroll)
        layout.addLayout(button_layout)
        
        # Connect buttons
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
    
   
    def update_coordinates(self, lat, lng):
        """Update the coordinate fields"""
        self.latitude.setText(str(lat))
        self.longitude.setText(str(lng))
    
    def get_data(self):
        """Get the form data"""
        return {
            'name': self.name.text(),
            'type': self.type.currentData(),
            'status': self.status.currentData(),
            'lon': float(self.longitude.text()) if self.longitude.text() else None,
            'lat': float(self.latitude.text()) if self.latitude.text() else None,
            'ground_elevation': float(self.elevation.text()) if self.elevation.text() else None,
            'final_depth': float(self.final_depth.text()) if self.final_depth.text() else None,
            'start_date': self.start_date.text(),
            'end_date': self.end_date.text(),
            'purpose': self.purpose.text(),
            'method': self.method.text(),
            'termination_reason': self.termination_reason.text(),
            'letter_grid_ref': self.letter_grid_ref.text(),
            'local_x': float(self.local_x.text()) if self.local_x.text() else None,
            'local_y': float(self.local_y.text()) if self.local_y.text() else None,
            'local_z': float(self.local_z.text()) if self.local_z.text() else None,
            'local_grid_ref_system': self.local_grid_ref_system.text(),
            'local_datum_system': self.local_datum_system.text(),
            'easting_end_traverse': float(self.easting_end_traverse.text()) if self.easting_end_traverse.text() else None,
            'northing_end_traverse': float(self.northing_end_traverse.text()) if self.northing_end_traverse.text() else None,
            'ground_level_end_traverse': float(self.ground_level_end_traverse.text()) if self.ground_level_end_traverse.text() else None,
            'local_x_end_traverse': float(self.local_x_end_traverse.text()) if self.local_x_end_traverse.text() else None,
            'local_y_end_traverse': float(self.local_y_end_traverse.text()) if self.local_y_end_traverse.text() else None,
            'local_z_end_traverse': float(self.local_z_end_traverse.text()) if self.local_z_end_traverse.text() else None,
            'end_lat': float(self.end_lat.text()) if self.end_lat.text() else None,
            'end_lon': float(self.end_lon.text()) if self.end_lon.text() else None,
            'projection_format': self.projection_format.text(),
            'sub_division': self.sub_division.text(),
            'phase_grouping_code': self.phase_grouping_code.text(),
            'alignment_id': int(self.alignment_id.text()) if self.alignment_id.text() else None,
            'offset': float(self.offset.text()) if self.offset.text() else None,
            'chainage': float(self.chainage.text()) if self.chainage.text() else None,
            'algorithm_ref': self.algorithm_ref.text(),
            'file_reference': self.file_reference.text(),
            'national_datum_system': self.national_datum_system.text(),
            'original_hole_id': self.original_hole_id.text(),
            'original_job_ref': self.original_job_ref.text(),
            'originating_company': self.originating_company.text(),
            'remarks': self.remarks.text()
        }