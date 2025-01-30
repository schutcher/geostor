from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QComboBox, QMessageBox,
    QLabel, QWidget
)
from PySide6.QtCore import Qt, Signal
from datetime import datetime

class EditSampleDialog(QDialog):
    """Dialog for editing a single sample"""
    
    sample_updated = Signal(dict)  # Signal emitted when sample is updated
    
    def __init__(self, parent=None, sample=None, project=None, db=None):
        super().__init__(parent)
        self.sample = sample
        self.project = project
        self.db = db
        self.locations = []
        if project:
            self.locations = [(loc.name, loc.id) for loc in project.locations]
        self.setup_ui()
        if sample:
            self.load_sample_data()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Edit Sample")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Location selection
        self.location_combo = QComboBox()
        self.location_combo.setPlaceholderText("Select Location")
        for name, id in self.locations:
            self.location_combo.addItem(name, id)
        form_layout.addRow("Location:", self.location_combo)
        
        # Reference
        self.reference_edit = QLineEdit()
        form_layout.addRow("Reference:", self.reference_edit)
        
        # Type selection
        self.type_combo = QComboBox()
        self.type_combo.setPlaceholderText("Select Type")
        self.type_combo.addItem("", None)  # Add empty option
        if self.db:
            type_abbrs = self.db.get_ags_abbreviations("SAMP_TYPE")
            for abbr in type_abbrs:
                self.type_combo.addItem(f"{abbr.abbr_code} - {abbr.abbr_description}", abbr.abbr_code)
        form_layout.addRow("Type:", self.type_combo)
        
        # Depths
        self.top_depth_edit = QLineEdit()
        self.bottom_depth_edit = QLineEdit()
        form_layout.addRow("Top Depth:", self.top_depth_edit)
        form_layout.addRow("Bottom Depth:", self.bottom_depth_edit)
        
        # Description and remarks
        self.description_edit = QLineEdit()
        self.remarks_edit = QLineEdit()
        form_layout.addRow("Description:", self.description_edit)
        form_layout.addRow("Remarks:", self.remarks_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_sample)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        # Add layouts to main layout
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        
    def load_sample_data(self):
        """Load the sample data into the form"""
        # Set location
        index = self.location_combo.findData(self.sample.location_id)
        if index >= 0:
            self.location_combo.setCurrentIndex(index)
            
        # Set other fields
        self.reference_edit.setText(self.sample.reference)
        
        if self.sample.type:
            index = self.type_combo.findData(self.sample.type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
                
        if self.sample.top_depth is not None:
            self.top_depth_edit.setText(str(self.sample.top_depth))
        if self.sample.bottom_depth is not None:
            self.bottom_depth_edit.setText(str(self.sample.bottom_depth))
            
        if self.sample.description:
            self.description_edit.setText(self.sample.description)
        if self.sample.remarks:
            self.remarks_edit.setText(self.sample.remarks)
        
    def save_sample(self):
        """Save the sample changes"""
        location_id = self.location_combo.currentData()
        if location_id is None:
            QMessageBox.warning(self, "Error", "Please select a location")
            return
            
        reference = self.reference_edit.text().strip()
        if not reference:
            QMessageBox.warning(self, "Error", "Sample reference is required")
            return
            
        # Get other fields
        sample_type = self.type_combo.currentData()
        
        # Convert depths
        try:
            top_depth = self.top_depth_edit.text().strip()
            bottom_depth = self.bottom_depth_edit.text().strip()
            top_depth = float(top_depth) if top_depth else None
            bottom_depth = float(bottom_depth) if bottom_depth else None
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid depth value")
            return
            
        # Create update data
        data = {
            'id': self.sample.id,
            'location_id': location_id,
            'reference': reference,
            'type': sample_type,
            'top_depth': top_depth,
            'bottom_depth': bottom_depth,
            'description': self.description_edit.text().strip(),
            'remarks': self.remarks_edit.text().strip(),
            'updated_at': datetime.utcnow()
        }
        
        self.sample_updated.emit(data)
        self.accept()
