from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel,
    QComboBox, QMessageBox, QWidget
)
from PySide6.QtCore import Qt

class ProjectDialog(QDialog):
    """Dialog for project selection, creation, and editing"""
    
    def __init__(self, db, mode="select", project_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.mode = mode
        self.project_id = project_id
        self.selected_project_id = None
        
        if mode == "select":
            self.setWindowTitle("Select Project")
        elif mode == "create":
            self.setWindowTitle("Create New Project")
        else:
            self.setWindowTitle("Edit Project")
        
        self.setup_ui()
        
        # Load project data if editing
        if mode == "edit" and project_id:
            self.load_project(project_id)
    
    def setup_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        
        if self.mode == "select":
            # Project selection combo box
            self.project_combo = QComboBox()
            self.refresh_project_list()
            layout.addWidget(QLabel("Select a project:"))
            layout.addWidget(self.project_combo)
        else:
            # Project form
            form_widget = QWidget()
            self.form_layout = QFormLayout(form_widget)
            
            self.name_edit = QLineEdit()
            self.form_layout.addRow("Name*:", self.name_edit)
            
            self.number_edit = QLineEdit()
            self.form_layout.addRow("Number:", self.number_edit)
            
            self.location_edit = QLineEdit()
            self.form_layout.addRow("Location:", self.location_edit)
            
            self.client_edit = QLineEdit()
            self.form_layout.addRow("Client:", self.client_edit)
            
            self.contractor_edit = QLineEdit()
            self.form_layout.addRow("Contractor:", self.contractor_edit)
            
            self.engineer_edit = QLineEdit()
            self.form_layout.addRow("Engineer:", self.engineer_edit)
            
            self.memo_edit = QTextEdit()
            self.memo_edit.setMaximumHeight(100)
            self.form_layout.addRow("Memo:", self.memo_edit)
            
            layout.addWidget(form_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        if self.mode == "select":
            self.ok_btn = QPushButton("Select")
        elif self.mode == "create":
            self.ok_btn = QPushButton("Create")
        else:
            self.ok_btn = QPushButton("Save")
        
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setDefault(True)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
    
    def refresh_project_list(self):
        """Refresh the project combo box"""
        self.project_combo.clear()
        projects = self.db.get_all_projects()
        
        for project in projects:
            self.project_combo.addItem(project.name, project.id)
    
    def load_project(self, project_id):
        """Load project data into form"""
        project = self.db.get_project(project_id)
        if not project:
            return
        
        self.name_edit.setText(project.name)
        self.number_edit.setText(project.number or "")
        self.location_edit.setText(project.location or "")
        self.client_edit.setText(project.client or "")
        self.contractor_edit.setText(project.contractor or "")
        self.engineer_edit.setText(project.engineer or "")
        self.memo_edit.setText(project.memo or "")
    
    def get_form_data(self):
        """Get data from form fields"""
        return {
            'name': self.name_edit.text().strip(),
            'number': self.number_edit.text().strip() or None,
            'location': self.location_edit.text().strip() or None,
            'client': self.client_edit.text().strip() or None,
            'contractor': self.contractor_edit.text().strip() or None,
            'engineer': self.engineer_edit.text().strip() or None,
            'memo': self.memo_edit.toPlainText().strip() or None
        }
    
    def validate_form(self):
        """Validate form data"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Project name is required")
            self.name_edit.setFocus()
            return False
        return True
    
    def accept(self):
        """Handle dialog acceptance"""
        if self.mode == "select":
            # Get selected project ID
            index = self.project_combo.currentIndex()
            if index >= 0:
                self.selected_project_id = self.project_combo.itemData(index)
                super().accept()
            else:
                QMessageBox.warning(self, "Error", "Please select a project")
        else:
            # Create or edit project
            if not self.validate_form():
                return
            
            data = self.get_form_data()
            
            if self.mode == "create":
                success, message, project_id = self.db.create_project(**data)
                if success:
                    self.selected_project_id = project_id
                    super().accept()
                else:
                    QMessageBox.warning(self, "Error", message)
            else:
                success, message = self.db.update_project(self.project_id, **data)
                if success:
                    super().accept()
                else:
                    QMessageBox.warning(self, "Error", message)
