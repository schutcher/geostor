from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QInputDialog, QWizard, QDialog,
    QPushButton, QStackedWidget, QFrame
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSettings
import os
import shutil
from pathlib import Path

from ..dialogs.database_wizard import DatabaseWizard
from ..dialogs.project_dialog import ProjectDialog
from ...database.operations import DatabaseOperations
from ...database.init_db import initialize_database

# Import views
from ..views.project_view import ProjectView
from ..views.locations_view import LocationsView
from ..views.samples_view import SamplesView
from ..views.geology_view import GeologyView
from ..views.laboratory_view import LaboratoryView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_db_path = None
        self.current_project_id = None
        self.current_project_name = None
        self.db_ops = None
        
        self.setWindowTitle("Geotechnical Data Manager")
        self.setGeometry(100, 100, 1200, 800)
        
        self.settings = QSettings("GeoTech", "DataManager")
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Create sidebar and content area
        self.create_sidebar()
        self.create_content_area()
        self.create_menu()
        
        # Try to connect to last used database
        last_db = self.settings.value("last_database")
        if last_db and os.path.exists(last_db):
            self.connect_database(last_db)
    
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFrameStyle(QFrame.StyledPanel)
        sidebar.setMaximumWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Status section
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_layout = QVBoxLayout(status_frame)
        
        # Connection status
        self.connection_status = QLabel("Not Connected")
        self.connection_status.setStyleSheet("color: red;")
        status_layout.addWidget(self.connection_status)
        
        # Project status
        self.project_status = QLabel("No Project Selected")
        status_layout.addWidget(self.project_status)
        
        sidebar_layout.addWidget(status_frame)
        
        # Navigation buttons
        self.nav_buttons = {}
        
        # Add Project button first
        project_btn = QPushButton("Project")
        project_btn.setCheckable(True)
        project_btn.clicked.connect(lambda checked: self.switch_view("Project"))
        sidebar_layout.addWidget(project_btn)
        self.nav_buttons["Project"] = project_btn
        
        # Add other navigation buttons
        for view_name in ["Locations", "Samples", "Geology", "Laboratory"]:
            btn = QPushButton(view_name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, name=view_name: self.switch_view(name))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[view_name] = btn
        
        sidebar_layout.addStretch()
        self.main_layout.addWidget(sidebar)
    
    def create_content_area(self):
        self.stack = QStackedWidget()
        
        # Create views without database connection initially
        self.views = {
            "Project": None,  # Will be initialized when database is connected
            "Locations": LocationsView(),
            "Samples": SamplesView(),
            "Geology": GeologyView(),
            "Laboratory": LaboratoryView()
        }
        
        # Add placeholder widgets
        for name, view in self.views.items():
            if view:  # Skip None values
                self.stack.addWidget(view)
        
        self.main_layout.addWidget(self.stack, stretch=1)
    
    def switch_view(self, view_name):
        """Switch to the selected view"""
        # Update button states
        for name, btn in self.nav_buttons.items():
            btn.setChecked(name == view_name)
        
        # Get the view
        view = self.views[view_name]
        
        # Check if we can switch to this view
        if view_name != "Project" and not self.current_project_id:
            QMessageBox.warning(
                self,
                "No Project Selected",
                "Please select a project before accessing this view."
            )
            # Reset button state
            self.nav_buttons[view_name].setChecked(False)
            self.nav_buttons["Project"].setChecked(True)
            return
        
        # Switch to the view
        if view:
            # Call on_hide for current view
            current_view = self.stack.currentWidget()
            if current_view and hasattr(current_view, 'on_hide'):
                current_view.on_hide()
            
            # Switch to new view
            self.stack.setCurrentWidget(view)
            
            # Call on_show for new view
            if hasattr(view, 'on_show'):
                view.on_show()
        else:
            QMessageBox.warning(
                self,
                "View Not Available",
                f"The {view_name} view is not available. Please connect to a database first."
            )
            # Reset button state
            self.nav_buttons[view_name].setChecked(False)
    
    def update_project_status(self):
        if self.current_project_id and self.current_project_name:
            self.project_status.setText(f"Project: {self.current_project_name}")
        else:
            self.project_status.setText("No Project Selected")
    
    def connect_database(self, db_path):
        """Connect to a database and initialize views"""
        try:
            self.current_db_path = db_path
            self.db_ops = DatabaseOperations(db_path)
            
            # Initialize ProjectView with database connection
            if self.views["Project"]:
                # Remove old view if it exists
                self.stack.removeWidget(self.views["Project"])
            
            self.views["Project"] = ProjectView(self.db_ops)
            self.views["Project"].project_selected.connect(self.on_project_selected)
            self.stack.insertWidget(0, self.views["Project"])  # Insert at the start
            
            # Initialize views with database connection
            if self.views["Locations"]:
                self.stack.removeWidget(self.views["Locations"])
            self.views["Locations"] = LocationsView(self.db_ops)
            self.stack.addWidget(self.views["Locations"])
            
            if self.views["Samples"]:
                self.stack.removeWidget(self.views["Samples"])
            self.views["Samples"] = SamplesView()
            self.stack.addWidget(self.views["Samples"])
            
            # Switch to project view
            self.stack.setCurrentWidget(self.views["Project"])
            self.nav_buttons["Project"].setChecked(True)
            
            # Update UI
            db_name = os.path.basename(db_path)
            self.connection_status.setText(f"Connected to {db_name}")
            self.connection_status.setStyleSheet("color: green;")
            
            # Save as last used database
            self.settings.setValue("last_database", db_path)
            self.add_recent_database(db_path)
            
            # Enable navigation
            for btn in self.nav_buttons.values():
                btn.setEnabled(True)
            
            # Update menu actions
            self.update_menu_actions()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Error connecting to database: {str(e)}")
            self.current_db_path = None
            self.db_ops = None
            return False
    
    def on_project_selected(self, project_id):
        """Handle project selection"""
        project = self.db_ops.get_project(project_id)
        if project:
            self.current_project_id = project_id
            self.current_project_name = project.name
            self.project_status.setText(f"Project: {project.name}")
            
            # Update views with new project
            if isinstance(self.views["Locations"], LocationsView):
                self.views["Locations"].set_project(project_id)
            if isinstance(self.views["Samples"], SamplesView):
                self.views["Samples"].set_project(project, self.db_ops)
            
            # Enable all navigation buttons
            for btn in self.nav_buttons.values():
                btn.setEnabled(True)
        else:
            self.current_project_id = None
            self.current_project_name = None
            self.project_status.setText("No Project Selected")
            
            # Disable all buttons except Project
            for name, btn in self.nav_buttons.items():
                btn.setEnabled(name == "Project")
    
    def select_project(self):
        dialog = ProjectDialog(self.db_ops, self)
        if dialog.exec() == QDialog.Accepted and dialog.selected_project:
            self.current_project_id = dialog.selected_project['id']
            self.current_project_name = dialog.selected_project['name']
            self.update_project_status()
            
            # Enable view navigation
            for btn in self.nav_buttons.values():
                btn.setEnabled(True)
            
            # Switch to Project view
            self.switch_view("Project")
    
    def create_menu(self):
        menu_bar = self.menuBar()
        
        # Database menu
        database_menu = menu_bar.addMenu("Database")
        
        # Create New Database action
        new_db_action = QAction("Create New Database", self)
        new_db_action.triggered.connect(lambda: self.launch_database_wizard("new"))
        database_menu.addAction(new_db_action)
        
        # Connect to Existing Database action
        connect_db_action = QAction("Connect to Existing Database", self)
        connect_db_action.triggered.connect(lambda: self.launch_database_wizard("existing"))
        database_menu.addAction(connect_db_action)
        
        database_menu.addSeparator()
        
        # Recent Databases submenu
        self.recent_menu = database_menu.addMenu("Recent Databases")
        self.update_recent_menu()
        
        database_menu.addSeparator()
        
        # Backup Database action
        backup_action = QAction("Backup Database", self)
        backup_action.setEnabled(False)
        backup_action.triggered.connect(self.backup_database)
        database_menu.addAction(backup_action)
        self.backup_action = backup_action
        
        # Reinitialize Database action
        reinitialize_action = QAction("Reinitialize Database", self)
        reinitialize_action.setEnabled(False)
        reinitialize_action.triggered.connect(self.reinitialize_database)
        database_menu.addAction(reinitialize_action)
        self.reinitialize_action = reinitialize_action
    
    def update_menu_actions(self):
        """Enable/disable menu actions based on database connection"""
        is_connected = self.current_db_path is not None
        self.backup_action.setEnabled(is_connected)
        self.reinitialize_action.setEnabled(is_connected)
    
    def launch_database_wizard(self, connection_type=None):
        wizard = DatabaseWizard(connection_type)
        if wizard.exec() == QWizard.Accepted:
            db_path = wizard.db_path
            self.connect_database(db_path)
    
    def add_recent_database(self, path: str):
        """Add a database to recent databases list and menu"""
        recent_dbs = self.settings.value("recent_databases", [])
        if not isinstance(recent_dbs, list):
            recent_dbs = []
        
        # Remove if already exists (to move it to top)
        if path in recent_dbs:
            recent_dbs.remove(path)
        
        # Add to beginning of list
        recent_dbs.insert(0, path)
        
        # Keep only last 10 entries
        recent_dbs = recent_dbs[:10]
        
        # Update settings
        self.settings.setValue("recent_databases", recent_dbs)
        
        # Update UI
        self.update_recent_menu()
    
    def update_recent_menu(self):
        """Update the Recent Databases submenu with the latest entries"""
        self.recent_menu.clear()
        recent_dbs = self.settings.value("recent_databases", [])
        
        for db_path in recent_dbs:
            if os.path.exists(db_path):
                action = QAction(os.path.basename(db_path), self)
                action.setData(db_path)
                action.triggered.connect(lambda checked, path=db_path: self.connect_database(path))
                self.recent_menu.addAction(action)
    
    def open_project(self, item):
        """Handle double-click on project item"""
        project_id = item.data(Qt.UserRole)
        if project_id is not None:
            self.current_project_id = project_id
            QMessageBox.information(self, "Project Selected", f"Selected project: {item.text()}")
            # TODO: Implement project opening logic
    
    def create_new_project(self):
        name, ok = QInputDialog.getText(
            self,
            "New Project",
            "Enter project name:",
            QLineEdit.Normal,
            ""
        )
        
        if ok and name:
            success, message, project_id = self.db_ops.create_project(name)
            
            if success:
                # Refresh the projects view
                self.update_projects_view()
                
                # Clear any existing search filter
                self.search_input.clear()
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Project '{name}' created successfully."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Database Error",
                    f"Failed to create project: {message}"
                )
    
    def backup_database(self):
        if not self.current_db_path:
            return
        
        try:
            backup_path = self.current_db_path + '.backup'
            shutil.copy2(self.current_db_path, backup_path)
            QMessageBox.information(
                self,
                "Backup Complete",
                f"Database backed up to: {backup_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Backup Failed",
                f"Failed to backup database: {str(e)}"
            )
    
    def reinitialize_database(self):
        """Reinitialize the database with updated schema"""
        if not self.current_db_path:
            return
            
        try:
            # Close current connection
            if self.db_ops:
                self.db_ops.close()
                self.db_ops = None
            
            # Create backup
            backup_path = self.current_db_path + '.backup'
            shutil.copy2(self.current_db_path, backup_path)
            
            # Initialize new database
            success, message = initialize_database(Path(self.current_db_path))
            if not success:
                # Restore backup
                shutil.copy2(backup_path, self.current_db_path)
                QMessageBox.critical(self, "Error", f"Failed to reinitialize database: {message}")
                return
            
            # Reconnect to database
            self.connect_database(self.current_db_path)
            QMessageBox.information(
                self,
                "Success",
                f"Database reinitialized successfully.\nA backup was created at: {backup_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reinitialize database: {str(e)}")
