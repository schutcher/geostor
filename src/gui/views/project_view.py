from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel,
    QDialog, QComboBox, QMessageBox, QToolBar,
    QStatusBar, QFrame
)
from PySide6.QtCore import Qt, Signal
from datetime import datetime

from .base_view import BaseView
from ..dialogs.project_dialog import ProjectDialog

class ProjectView(BaseView):
    """View for displaying and managing project information"""
    
    project_selected = Signal(int)  # Emitted when a project is selected
    
    def __init__(self, db, parent=None):
        self.db = db
        self.current_project_id = None
        super().__init__(parent)
    
    def setup_ui(self):
        """Initialize the UI components"""
        # Create toolbar
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Add toolbar buttons
        self.select_project_btn = QPushButton("Select Project")
        self.select_project_btn.clicked.connect(self.select_project)
        toolbar.addWidget(self.select_project_btn)
        
        self.new_project_btn = QPushButton("New Project")
        self.new_project_btn.clicked.connect(self.create_project)
        toolbar.addWidget(self.new_project_btn)
        
        self.edit_btn = QPushButton("Edit Project")
        self.edit_btn.clicked.connect(self.edit_project)
        self.edit_btn.setEnabled(False)
        toolbar.addWidget(self.edit_btn)
        
        self.main_layout.addWidget(toolbar)
        
        # Create status bar with additional info
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(5, 0, 5, 0)
        
        self.status_label = QLabel("No project selected")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        created_widget = QWidget()
        created_layout = QHBoxLayout(created_widget)
        created_layout.setContentsMargins(0, 0, 0, 0)
        created_layout.addWidget(QLabel("Created:"))
        self.created_label = QLabel()
        created_layout.addWidget(self.created_label)
        status_layout.addWidget(created_widget)
        
        status_layout.addSpacing(20)
        
        modified_widget = QWidget()
        modified_layout = QHBoxLayout(modified_widget)
        modified_layout.setContentsMargins(0, 0, 0, 0)
        modified_layout.addWidget(QLabel("Modified:"))
        self.updated_label = QLabel()
        modified_layout.addWidget(self.updated_label)
        status_layout.addWidget(modified_widget)
        
        # Add a line separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        
        self.main_layout.addWidget(separator)
        self.main_layout.addWidget(status_widget)
        self.main_layout.addWidget(separator)
        
        # Create form layout for project details
        form_widget = QWidget()
        self.form_layout = QFormLayout(form_widget)
        
        # Project fields
        self.name_edit = QLineEdit()
        self.name_edit.setReadOnly(True)
        self.form_layout.addRow("Name:", self.name_edit)
        
        self.number_edit = QLineEdit()
        self.number_edit.setReadOnly(True)
        self.form_layout.addRow("Number:", self.number_edit)
        
        self.location_edit = QLineEdit()
        self.location_edit.setReadOnly(True)
        self.form_layout.addRow("Location:", self.location_edit)
        
        self.client_edit = QLineEdit()
        self.client_edit.setReadOnly(True)
        self.form_layout.addRow("Client:", self.client_edit)
        
        self.contractor_edit = QLineEdit()
        self.contractor_edit.setReadOnly(True)
        self.form_layout.addRow("Contractor:", self.contractor_edit)
        
        self.engineer_edit = QLineEdit()
        self.engineer_edit.setReadOnly(True)
        self.form_layout.addRow("Engineer:", self.engineer_edit)
        
        self.memo_edit = QTextEdit()
        self.memo_edit.setReadOnly(True)
        self.memo_edit.setMaximumHeight(100)
        self.form_layout.addRow("Memo:", self.memo_edit)
        
        self.main_layout.addWidget(form_widget)
        self.main_layout.addStretch()
    
    def select_project(self):
        """Open dialog to select a project"""
        dialog = ProjectDialog(self.db, mode="select", parent=self)
        if dialog.exec() == QDialog.Accepted and dialog.selected_project_id is not None:
            self.load_project(dialog.selected_project_id)
    
    def create_project(self):
        """Open dialog to create a new project"""
        dialog = ProjectDialog(self.db, mode="create", parent=self)
        if dialog.exec() == QDialog.Accepted and dialog.selected_project_id is not None:
            self.load_project(dialog.selected_project_id)
    
    def edit_project(self):
        """Open dialog to edit current project"""
        if not self.current_project_id:
            return
            
        dialog = ProjectDialog(self.db, mode="edit", project_id=self.current_project_id, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_project(self.current_project_id)
    
    def load_project(self, project_id):
        """Load and display project data"""
        project = self.db.get_project(project_id)
        if not project:
            QMessageBox.warning(self, "Error", "Could not load project")
            return
        
        self.current_project_id = project_id
        
        # Update form fields
        self.name_edit.setText(project.name)
        self.number_edit.setText(project.number or "")
        self.location_edit.setText(project.location or "")
        self.client_edit.setText(project.client or "")
        self.contractor_edit.setText(project.contractor or "")
        self.engineer_edit.setText(project.engineer or "")
        self.memo_edit.setText(project.memo or "")
        
        # Update timestamps
        created_at = project.created_at.strftime("%Y-%m-%d %H:%M:%S") if project.created_at else "Unknown"
        updated_at = project.updated_at.strftime("%Y-%m-%d %H:%M:%S") if project.updated_at else "Unknown"
        
        self.created_label.setText(created_at)
        self.updated_label.setText(updated_at)
        
        # Enable edit button
        self.edit_btn.setEnabled(True)
        
        # Update status
        self.status_label.setText(f"Current project: {project.name}")
        
        # Emit signal
        self.project_selected.emit(project_id)
