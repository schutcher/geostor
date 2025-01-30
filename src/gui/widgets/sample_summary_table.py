from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from ...database.models import AGSAbbreviation

class SampleSummaryTable(QTableWidget):
    """A table widget for displaying sample summaries for a location"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the table UI"""
        # Set up headers
        headers = ["Type", "Top Depth", "Bottom Depth", "Description"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # Set header properties
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Type - allow resize for longer descriptions
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Top Depth
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Bottom Depth
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Description
        
        # Set selection behavior
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        
        # Make table read-only
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
    def get_type_description(self, session, type_code):
        """Get the description for a sample type code"""
        if not type_code:
            return ""
            
        abbr = session.query(AGSAbbreviation).filter(
            AGSAbbreviation.abbr_heading == "SAMP_TYPE",
            AGSAbbreviation.abbr_code == type_code
        ).first()
        
        return abbr.abbr_description if abbr else ""
        
    def update_samples(self, samples):
        """Update the table with new sample data"""
        self.setRowCount(0)
        if not samples:
            return
            
        # Get a session from the first sample's session
        session = samples[0].location.project._sa_instance_state.session
            
        for sample in samples:
            row = self.rowCount()
            self.insertRow(row)
            
            # Get type description
            type_code = sample.type
            type_desc = self.get_type_description(session, type_code)
            
            # Format type display
            type_text = type_code or ""
            if type_desc:
                type_text = f"{type_code} - {type_desc}" if type_code else type_desc
            
            # Add sample data
            self.setItem(row, 0, QTableWidgetItem(type_text))
            self.setItem(row, 1, QTableWidgetItem(str(sample.top_depth) if sample.top_depth is not None else ""))
            self.setItem(row, 2, QTableWidgetItem(str(sample.bottom_depth) if sample.bottom_depth is not None else ""))
            self.setItem(row, 3, QTableWidgetItem(sample.description or ""))
            
            # Make cells read-only
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        # Resize type column to fit content
        self.resizeColumnToContents(0)
