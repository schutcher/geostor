from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QComboBox, QMessageBox,
    QWidget, QTableWidget, QTableWidgetItem, QLabel,
    QHeaderView
)
from PySide6.QtCore import Qt, Signal
from datetime import datetime

class SampleTypeComboDelegate(QComboBox):
    """Custom ComboBox delegate for sample types in the table"""
    def __init__(self, parent=None, type_options=None):
        super().__init__(parent)
        # Add empty option first
        self.addItem("", None)
        if type_options:
            for code, description in type_options:
                self.addItem(f"{code} - {description}", code)
        
        # Set placeholder text
        self.setPlaceholderText("Select Type")

class SampleTableWidget(QTableWidget):
    """Custom table widget that automatically adds a new row when the last row is edited"""
    
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.type_options = []
        if db:
            type_abbrs = db.get_ags_abbreviations("SAMP_TYPE")
            self.type_options = [(abbr.abbr_code, abbr.abbr_description) for abbr in type_abbrs]
        self.setup_table()
        
    def setup_table(self):
        """Setup the table columns and properties"""
        headers = ["Reference", "Type", "Top Depth", "Bottom Depth", "Description", "Remarks"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.add_empty_row()
        
    def add_empty_row(self):
        """Add a new empty row to the table"""
        row = self.rowCount()
        self.insertRow(row)
        
        # Add items for each column
        for col in range(self.columnCount()):
            if col == 1:  # Type column
                combo = SampleTypeComboDelegate(self, self.type_options)
                self.setCellWidget(row, col, combo)
            else:
                self.setItem(row, col, QTableWidgetItem(""))
            
    def item_changed(self, item):
        """Called when a table item is changed"""
        if not item:
            return
            
        # Only add a new row if this is the last row and any cell in the row has data
        if item.row() == self.rowCount() - 1:
            row_has_data = False
            for col in range(self.columnCount()):
                if col == 1:  # Type column
                    combo = self.cellWidget(item.row(), col)
                    if combo and combo.currentData() is not None:
                        row_has_data = True
                        break
                else:
                    cell_item = self.item(item.row(), col)
                    if cell_item and cell_item.text().strip():
                        row_has_data = True
                        break
            
            if row_has_data:
                self.add_empty_row()
            
    def get_row_data(self, row):
        """Get data from a specific row, handling the combo box for type"""
        data = {}
        
        # Get reference
        reference_item = self.item(row, 0)
        if reference_item:
            data['reference'] = reference_item.text().strip()
        
        # Get type from combo box
        type_combo = self.cellWidget(row, 1)
        if type_combo:
            data['type'] = type_combo.currentData()
        
        # Get other fields
        for col, field in enumerate(['top_depth', 'bottom_depth', 'description', 'remarks']):
            item = self.item(row, col + 2)
            if item:
                data[field] = item.text().strip()
            
        return data
    
    def has_data(self, row):
        """Check if a row has any data entered"""
        # Check reference
        ref_item = self.item(row, 0)
        if ref_item and ref_item.text().strip():
            return True
            
        # Check type
        type_combo = self.cellWidget(row, 1)
        if type_combo and type_combo.currentData() is not None:
            return True
            
        # Check other fields
        for col in range(2, self.columnCount()):
            item = self.item(row, col)
            if item and item.text().strip():
                return True
                
        return False

class SampleDialog(QDialog):
    """Dialog for adding multiple samples at once"""
    
    samples_added = Signal(list)  # Signal emitted when samples are added successfully
    
    def __init__(self, parent=None, project=None, db=None):
        super().__init__(parent)
        self.project = project
        self.db = db
        self.locations = []
        if project:
            self.locations = [(loc.name, loc.id) for loc in project.locations]
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Add Samples")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout(self)
        
        # Location selection
        location_layout = QHBoxLayout()
        location_label = QLabel("Location:")
        self.location_combo = QComboBox()
        self.location_combo.setPlaceholderText("Select Location")
        for name, id in self.locations:
            self.location_combo.addItem(name, id)
        location_layout.addWidget(location_label)
        location_layout.addWidget(self.location_combo)
        location_layout.addStretch()
        
        # Sample table
        self.table = SampleTableWidget(self, self.db)
        self.table.itemChanged.connect(self.table.item_changed)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_samples)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        # Add all components to main layout
        layout.addLayout(location_layout)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
                
    def save_samples(self):
        """Save all samples in the table"""
        location_id = self.location_combo.currentData()
        if location_id is None:
            QMessageBox.warning(self, "Error", "Please select a location")
            return
            
        samples = []
        for row in range(self.table.rowCount()):
            # Skip rows with no data
            if not self.table.has_data(row):
                continue
                
            # Get row data
            data = self.table.get_row_data(row)
            
            # Validate reference
            if not data.get('reference'):
                QMessageBox.warning(self, "Error", f"Sample reference is required for row {row + 1}")
                return
                
            # Convert depths to float if provided
            try:
                top_depth = data.get('top_depth')
                bottom_depth = data.get('bottom_depth')
                data['top_depth'] = float(top_depth) if top_depth else None
                data['bottom_depth'] = float(bottom_depth) if bottom_depth else None
            except ValueError:
                QMessageBox.warning(self, "Error", f"Invalid depth value in row {row + 1}")
                return
                
            # Add location_id and timestamps
            data['location_id'] = location_id
            data['created_at'] = datetime.utcnow()
            data['updated_at'] = datetime.utcnow()
            
            samples.append(data)
            
        if not samples:
            QMessageBox.warning(self, "Error", "No samples to save")
            return
            
        self.samples_added.emit(samples)
        self.accept()
