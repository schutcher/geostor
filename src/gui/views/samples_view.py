from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox
)
from PySide6.QtCore import Qt
from .base_view import BaseView
from ..dialogs.sample_dialog import SampleDialog
from ..dialogs.edit_sample_dialog import EditSampleDialog
from src.database.models import Sample, Project, Location, AGSAbbreviation
from sqlalchemy.orm import joinedload

class SamplesView(BaseView):
    def __init__(self, parent=None):
        self.current_project_id = None
        self.db = None
        super().__init__(parent)
        self.setObjectName("SamplesView")
    
    def setup_ui(self):
        """Setup the view's UI"""
        # Header with title and buttons
        header_layout = QHBoxLayout()
        title = QLabel("Samples")
        title.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Add button
        self.add_button = QPushButton("Add Samples")
        self.add_button.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(self.add_button)
        
        # Edit button
        self.edit_button = QPushButton("Edit Sample")
        self.edit_button.clicked.connect(self.edit_selected_sample)
        self.edit_button.setEnabled(False)
        header_layout.addWidget(self.edit_button)
        
        # Delete button
        self.delete_button = QPushButton("Delete Sample")
        self.delete_button.clicked.connect(self.delete_selected_sample)
        self.delete_button.setEnabled(False)
        header_layout.addWidget(self.delete_button)
        
        # Samples table
        self.table = QTableWidget()
        self.setup_table()
        
        # Add components to main layout
        self.main_layout.addLayout(header_layout)
        self.main_layout.addWidget(self.table)
        
    def setup_table(self):
        """Setup the samples table"""
        headers = ["ID", "Location", "Reference", "Type", "Top Depth", "Bottom Depth", "Description", "Remarks"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # Set column resize modes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Location
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Reference
        header.setSectionResizeMode(3, QHeaderView.Interactive)  # Type - allow resize for descriptions
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Top Depth
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Bottom Depth
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Description
        header.setSectionResizeMode(7, QHeaderView.Stretch)  # Remarks
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        # Hide the ID column
        self.table.setColumnHidden(0, True)
        
    def get_type_description(self, session, type_code):
        """Get the description for a sample type code"""
        if not type_code:
            return ""
            
        abbr = session.query(AGSAbbreviation).filter(
            AGSAbbreviation.abbr_heading == "SAMP_TYPE",
            AGSAbbreviation.abbr_code == type_code
        ).first()
        
        return abbr.abbr_description if abbr else ""

    def set_project(self, project, db):
        """Set the current project and refresh the view"""
        self.current_project_id = project.id
        self.db = db
        self.refresh_samples()
        
    def refresh_samples(self):
        """Refresh the samples table with current project data"""
        self.table.setRowCount(0)
        if not self.current_project_id or not self.db:
            return
            
        # Get fresh project data with locations and samples
        session = self.db.get_session()
        try:
            project = session.query(Project).options(
                joinedload(Project.locations).joinedload(Location.samples)
            ).get(self.current_project_id)
            
            if not project:
                return
                
            # Collect all samples from all locations
            row = 0
            for location in project.locations:
                for sample in location.samples:
                    self.table.insertRow(row)
                    
                    # Get type description
                    type_code = sample.type
                    type_desc = self.get_type_description(session, type_code)
                    
                    # Format type display
                    type_text = type_code or ""
                    if type_desc:
                        type_text = f"{type_code} - {type_desc}" if type_code else type_desc
                    
                    # Add sample data
                    self.table.setItem(row, 0, QTableWidgetItem(str(sample.id)))
                    self.table.setItem(row, 1, QTableWidgetItem(location.name))
                    self.table.setItem(row, 2, QTableWidgetItem(sample.reference))
                    self.table.setItem(row, 3, QTableWidgetItem(type_text))
                    self.table.setItem(row, 4, QTableWidgetItem(str(sample.top_depth) if sample.top_depth is not None else ""))
                    self.table.setItem(row, 5, QTableWidgetItem(str(sample.bottom_depth) if sample.bottom_depth is not None else ""))
                    self.table.setItem(row, 6, QTableWidgetItem(sample.description or ""))
                    self.table.setItem(row, 7, QTableWidgetItem(sample.remarks or ""))
                    
                    # Make cells read-only
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
                    row += 1
                    
            # Resize type column to fit content
            self.table.resizeColumnToContents(3)
        finally:
            session.close()
            
    def on_selection_changed(self):
        """Handle table selection changes"""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
    
    def get_selected_sample_id(self):
        """Get the ID of the selected sample"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        return int(self.table.item(row, 0).text())
    
    def show_add_dialog(self):
        """Show the dialog to add new samples"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Error", "Please select a project first")
            return
            
        # Get fresh project data for the dialog
        session = self.db.get_session()
        try:
            project = session.query(Project).options(
                joinedload(Project.locations)
            ).get(self.current_project_id)
            
            if not project:
                QMessageBox.warning(self, "Error", "Could not load project data")
                return
                
            dialog = SampleDialog(self, project, self.db)
            dialog.samples_added.connect(self.add_samples)
            dialog.exec()
        finally:
            session.close()
    
    def edit_selected_sample(self):
        """Edit the selected sample"""
        sample_id = self.get_selected_sample_id()
        if not sample_id:
            return
            
        # Get the sample and project data
        sample = self.db.get_sample(sample_id)
        if not sample:
            QMessageBox.warning(self, "Error", "Could not load sample data")
            return
            
        session = self.db.get_session()
        try:
            project = session.query(Project).options(
                joinedload(Project.locations)
            ).get(self.current_project_id)
            
            if not project:
                QMessageBox.warning(self, "Error", "Could not load project data")
                return
                
            dialog = EditSampleDialog(self, sample, project, self.db)
            dialog.sample_updated.connect(self.update_sample)
            dialog.exec()
        finally:
            session.close()
    
    def delete_selected_sample(self):
        """Delete the selected sample"""
        sample_id = self.get_selected_sample_id()
        if not sample_id:
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this sample?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.db.delete_sample(sample_id)
            if success:
                self.refresh_samples()
            else:
                QMessageBox.warning(self, "Error", message)
        
    def add_samples(self, samples_data):
        """Add new samples to the database"""
        session = self.db.get_session()
        try:
            for data in samples_data:
                sample = Sample(**data)
                session.add(sample)
            session.commit()
            self.refresh_samples()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Failed to add samples: {str(e)}")
        finally:
            session.close()
            
    def update_sample(self, data):
        """Update a sample in the database"""
        sample_id = data.pop('id')
        success, message = self.db.update_sample(sample_id, **data)
        if success:
            self.refresh_samples()
        else:
            QMessageBox.warning(self, "Error", message)
