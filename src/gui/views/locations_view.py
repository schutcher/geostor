from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QFrame, QHeaderView, QSplitter,
    QLabel, QPushButton, QToolBar, QMessageBox, QDialog,
    QTabWidget
)
from PySide6.QtCore import Qt, QObject, Slot, Signal
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
import os
import atexit
import json

from .base_view import BaseView
from ..dialogs.location_dialog import LocationDialog
from ..map_utils import get_map_html_template
from ..widgets.sample_summary_table import SampleSummaryTable
from sqlalchemy.orm import joinedload
from ...database.models import Location

class Bridge(QObject):
    """Bridge class for JavaScript communication"""
    markerClicked = Signal(str)  # Signal to emit when a marker is clicked
    mapClicked = Signal(float, float)  # Signal to emit when the map is clicked
    markerMoved = Signal(str, float, float)  # Signal to emit when a marker is moved

    @Slot(str)
    def on_marker_click(self, location_id):
        self.markerClicked.emit(location_id)

    @Slot(float, float)
    def on_map_clicked(self, lat, lng):
        self.mapClicked.emit(lat, lng)

    @Slot(str, float, float)
    def on_marker_moved(self, location_id, lat, lng):
        self.markerMoved.emit(location_id, lat, lng)

class LocationsView(BaseView):
    """View for displaying and managing locations"""
    
    def __init__(self, db=None, parent=None):
        self.db = db
        self.temp_files = []
        self.add_point_mode = False
        self.project_id = None
        self.move_mode = False
        self.selected_location = None        
        super().__init__(parent)
        
        # Set up WebChannel for JavaScript communication
        self.bridge = Bridge()
        self.bridge.markerClicked.connect(self.on_marker_clicked)
        self.bridge.mapClicked.connect(self.on_map_clicked)
        self.bridge.markerMoved.connect(self.on_marker_moved)
        self.channel = QWebChannel()
        self.channel.registerObject('bridge', self.bridge)
        self.map_view.page().setWebChannel(self.channel)
        
        # Store current dialog
        self.current_dialog = None
        
        # Register cleanup on exit
        atexit.register(self.cleanup_temp_files)
    
    def set_project(self, project_id):
        """Set the current project and update locations"""
        self.project_id = project_id
        self.update_locations()
    
    def cleanup_temp_files(self):
        """Clean up any remaining temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        self.temp_files.clear()
    
    def setup_ui(self):
        """Initialize the UI components"""
        # Create top and bottom splitter
        self.vertical_splitter = QSplitter(Qt.Vertical)
        
        # Create top widget
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create horizontal splitter for table and map
        self.horizontal_splitter = QSplitter(Qt.Horizontal)
        
        # Create left frame for table
        table_frame = QFrame()
        table_frame.setFrameStyle(QFrame.StyledPanel)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add table toolbar
        table_toolbar = QToolBar()
        self.add_location_btn = QPushButton("Add Location")
        self.edit_location_btn = QPushButton("Edit Location")
        self.move_location_btn = QPushButton("Move Location")
        self.move_location_btn.setCheckable(True)
        self.move_location_btn.toggled.connect(self.toggle_move_mode)
        self.move_location_btn.setEnabled(False)  # Initially disabled
        self.delete_location_btn = QPushButton("Delete Location")
        self.import_locations_btn = QPushButton("Import Locations")
        
        table_toolbar.addWidget(self.add_location_btn)
        table_toolbar.addWidget(self.edit_location_btn)
        table_toolbar.addWidget(self.move_location_btn)  # Add to toolbar
        table_toolbar.addWidget(self.delete_location_btn)
        table_toolbar.addWidget(self.import_locations_btn)
        
        table_layout.addWidget(table_toolbar)
        
        # Create locations table
        self.locations_table = QTableWidget()
        self.setup_locations_table()
        table_layout.addWidget(self.locations_table)
        
        # Create right frame for map
        map_frame = QFrame()
        map_frame.setFrameStyle(QFrame.StyledPanel)
        map_layout = QVBoxLayout(map_frame)
        map_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add map toolbar
        map_toolbar = QToolBar()
        self.add_point_btn = QPushButton("Add Point")
        self.add_point_btn.setCheckable(True)
        map_toolbar.addWidget(self.add_point_btn)
        map_layout.addWidget(map_toolbar)
        
        # Create map view
        self.map_view = QWebEngineView()
        self.setup_map()
        map_layout.addWidget(self.map_view)
        
        # Add frames to horizontal splitter
        self.horizontal_splitter.addWidget(table_frame)
        self.horizontal_splitter.addWidget(map_frame)
        
        # Set the split ratio (60/40)
        total_width = self.width()
        self.horizontal_splitter.setSizes([int(total_width * 0.6), int(total_width * 0.4)])
        
        # Add horizontal splitter to top layout
        top_layout.addWidget(self.horizontal_splitter)
        
        # Create bottom widget for data summary
        bottom_widget = QFrame()
        bottom_widget.setFrameStyle(QFrame.StyledPanel)
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add title for summary section
        summary_title = QLabel("Location Data Summary")
        summary_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        bottom_layout.addWidget(summary_title)
        
        # Create tab widget for different summaries
        self.summary_tabs = QTabWidget()
        
        # Create and add sample summary tab
        self.sample_summary = SampleSummaryTable()
        self.summary_tabs.addTab(self.sample_summary, "Samples")
        
        # Add tab widget to bottom layout
        bottom_layout.addWidget(self.summary_tabs)
        
        # Add widgets to vertical splitter
        self.vertical_splitter.addWidget(top_widget)
        self.vertical_splitter.addWidget(bottom_widget)
        
        # Set the vertical split ratio (70/30)
        total_height = self.height()
        self.vertical_splitter.setSizes([int(total_height * 0.7), int(total_height * 0.3)])
        
        # Add splitter to main layout
        self.main_layout.addWidget(self.vertical_splitter)
        
        # Connect button signals
        self.add_location_btn.clicked.connect(self.add_location)
        self.edit_location_btn.clicked.connect(self.edit_location)
        self.delete_location_btn.clicked.connect(self.delete_location)
        self.import_locations_btn.clicked.connect(self.import_locations)
        self.add_point_btn.clicked.connect(self.toggle_add_point_mode)
        
        # Initially disable edit and delete buttons
        self.edit_location_btn.setEnabled(False)
        self.delete_location_btn.setEnabled(False)
        
        # Connect table selection
        self.locations_table.itemSelectionChanged.connect(self.on_selection_changed)

    def setup_locations_table(self):
        """Setup the locations table with all fields"""
        # Define columns
        columns = [
            'Name', 'Type', 'Status', 'Longitude', 'Latitude',
            'Ground Elevation', 'Final Depth', 'Start Date', 'End Date',
            'Purpose', 'Method', 'Termination Reason', 'Letter Grid Ref',
            'Local X', 'Local Y', 'Local Z', 'Local Grid System', 'Local Datum System',
            'Easting End Traverse', 'Northing End Traverse', 'Ground Level End Traverse',
            'Local X End Traverse', 'Local Y End Traverse', 'Local Z End Traverse',
            'End Latitude', 'End Longitude', 'Projection Format', 'Sub Division',
            'Phase/Grouping Code', 'Alignment ID', 'Offset', 'Chainage',
            'Algorithm Reference', 'File Reference', 'National Datum System',
            'Original Hole ID', 'Original Job Reference', 'Originating Company', 'Remarks'
        ]
        
        self.locations_table.setColumnCount(len(columns))
        self.locations_table.setHorizontalHeaderLabels(columns)
        
        # Set column widths and resize mode
        header = self.locations_table.horizontalHeader()
        for i in range(len(columns)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        # Enable sorting
        self.locations_table.setSortingEnabled(True)
        
        # Enable selection of rows
        self.locations_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.locations_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Connect selection change to update map
        self.locations_table.itemSelectionChanged.connect(self.on_location_selected)
    
    def setup_map(self):
        """Setup the map with the HTML template"""
        html_template = get_map_html_template()
        self.map_view.setHtml(html_template)

    def toggle_move_mode(self, checked):
        """Toggle move mode for the selected location"""
        if not self.selected_location:
            self.move_location_btn.setChecked(False)
            QMessageBox.warning(self, "Error", "Please select a location to move")
            return
            
        location_id = self.selected_location.id
        self.move_mode = checked
        
        # Toggle marker dragging state
        self.map_view.page().runJavaScript(f'toggleMarkerDrag("{location_id}", {str(checked).lower()});')
        
        if checked:
            QMessageBox.information(
                self,
                "Move Location",
                "Drag the marker to the new location. Changes will be saved automatically."
            )

    @Slot(str, float, float)
    def on_marker_moved(self, location_id, lat, lng):
        """Handle marker movement and save to database immediately"""
        if not self.move_mode:
            return
        
        # Update the location in the database
        success, message = self.db.update_location(int(location_id), lat=lat, lon=lng)
        
        # Update the UI after database update is complete
        if success:
            self.update_locations()
            # Keep the marker draggable
            self.map_view.page().runJavaScript(f'toggleMarkerDrag("{location_id}", true);')
        else:
            QMessageBox.warning(self, "Error", f"Failed to update location: {message}")
            # Revert to original position on failure
            if self.selected_location and self.selected_location.lat and self.selected_location.lon:
                self.map_view.page().runJavaScript(
                    f'addMarker({self.selected_location.lat}, {self.selected_location.lon}, "{self.selected_location.name}", "{self.selected_location.id}");'
                )

    def update_locations(self):
        """Update the locations table and map with current project data"""
        if not self.project_id or not self.db:
            return
            
        # Clear existing data
        self.locations_table.setRowCount(0)
        
        # Get locations for current project
        locations = self.db.get_project_locations(self.project_id)
        
        # Update table
        for location in locations:
            row = self.locations_table.rowCount()
            self.locations_table.insertRow(row)
            
            # Create name item with ID stored in user role
            name_item = QTableWidgetItem(location.name)
            name_item.setData(Qt.UserRole, location.id)
            self.locations_table.setItem(row, 0, name_item)
            
            # Add other fields
            self.locations_table.setItem(row, 1, QTableWidgetItem(location.type or ""))
            self.locations_table.setItem(row, 2, QTableWidgetItem(location.status or ""))
            self.locations_table.setItem(row, 3, QTableWidgetItem(str(location.lon) if location.lon else ""))
            self.locations_table.setItem(row, 4, QTableWidgetItem(str(location.lat) if location.lat else ""))
            self.locations_table.setItem(row, 5, QTableWidgetItem(str(location.ground_elevation) if location.ground_elevation else ""))
            self.locations_table.setItem(row, 6, QTableWidgetItem(str(location.final_depth) if location.final_depth else ""))
            self.locations_table.setItem(row, 7, QTableWidgetItem(str(location.start_date) if location.start_date else ""))
            self.locations_table.setItem(row, 8, QTableWidgetItem(str(location.end_date) if location.end_date else ""))
            self.locations_table.setItem(row, 9, QTableWidgetItem(location.purpose or ""))
            self.locations_table.setItem(row, 10, QTableWidgetItem(location.method or ""))
            self.locations_table.setItem(row, 11, QTableWidgetItem(location.termination_reason or ""))
            self.locations_table.setItem(row, 12, QTableWidgetItem(location.letter_grid_ref or ""))
            self.locations_table.setItem(row, 13, QTableWidgetItem(str(location.local_x) if location.local_x else ""))
            self.locations_table.setItem(row, 14, QTableWidgetItem(str(location.local_y) if location.local_y else ""))
            self.locations_table.setItem(row, 15, QTableWidgetItem(str(location.local_z) if location.local_z else ""))
            self.locations_table.setItem(row, 16, QTableWidgetItem(location.local_grid_ref_system or ""))
            self.locations_table.setItem(row, 17, QTableWidgetItem(location.local_datum_system or ""))
            self.locations_table.setItem(row, 18, QTableWidgetItem(str(location.easting_end_traverse) if location.easting_end_traverse else ""))
            self.locations_table.setItem(row, 19, QTableWidgetItem(str(location.northing_end_traverse) if location.northing_end_traverse else ""))
            self.locations_table.setItem(row, 20, QTableWidgetItem(str(location.ground_level_end_traverse) if location.ground_level_end_traverse else ""))
            self.locations_table.setItem(row, 21, QTableWidgetItem(str(location.local_x_end_traverse) if location.local_x_end_traverse else ""))
            self.locations_table.setItem(row, 22, QTableWidgetItem(str(location.local_y_end_traverse) if location.local_y_end_traverse else ""))
            self.locations_table.setItem(row, 23, QTableWidgetItem(str(location.local_z_end_traverse) if location.local_z_end_traverse else ""))
            self.locations_table.setItem(row, 24, QTableWidgetItem(str(location.end_lat) if location.end_lat else ""))
            self.locations_table.setItem(row, 25, QTableWidgetItem(str(location.end_lon) if location.end_lon else ""))
            self.locations_table.setItem(row, 26, QTableWidgetItem(location.projection_format or ""))
            self.locations_table.setItem(row, 27, QTableWidgetItem(location.sub_division or ""))
            self.locations_table.setItem(row, 28, QTableWidgetItem(location.phase_grouping_code or ""))
            self.locations_table.setItem(row, 29, QTableWidgetItem(location.alignment_id or ""))
            self.locations_table.setItem(row, 30, QTableWidgetItem(str(location.offset) if location.offset else ""))
            self.locations_table.setItem(row, 31, QTableWidgetItem(str(location.chainage) if location.chainage else ""))
            self.locations_table.setItem(row, 32, QTableWidgetItem(location.algorithm_ref or ""))
            self.locations_table.setItem(row, 33, QTableWidgetItem(location.file_reference or ""))
            self.locations_table.setItem(row, 34, QTableWidgetItem(location.national_datum_system or ""))
            self.locations_table.setItem(row, 35, QTableWidgetItem(location.original_hole_id or ""))
            self.locations_table.setItem(row, 36, QTableWidgetItem(location.original_job_ref or ""))
            self.locations_table.setItem(row, 37, QTableWidgetItem(location.originating_company or ""))
            self.locations_table.setItem(row, 38, QTableWidgetItem(location.remarks or ""))
            
            # Make all cells read-only
            for col in range(self.locations_table.columnCount()):
                item = self.locations_table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        # Update map markers
        self.update_map_markers()
    
    def update_map_markers(self):
        """Update map with markers for all locations"""
        if not self.db:
            return
        
        # Clear existing markers
        self.map_view.page().runJavaScript("clearMarkers();")
        
        # Add markers for each location
        locations = self.db.get_project_locations(self.project_id)
        has_markers = False
        bounds = []
        
        for location in locations:
            if location.lat and location.lon:
                has_markers = True
                bounds.append([location.lat, location.lon])
                # Add marker using JavaScript
                js = f'addMarker({location.lat}, {location.lon}, "{location.name}", "{location.id}");'
                self.map_view.page().runJavaScript(js)
        
        # If we have markers, fit the map bounds to show all markers
        if has_markers:
            js_bounds = json.dumps(bounds)
            self.map_view.page().runJavaScript(f"fitBounds({js_bounds});")
    
    def on_location_selected(self):
        """Handle location selection in table"""
        selected_items = self.locations_table.selectedItems()
        if not selected_items:
            return
            
        # Get the selected row
        row = selected_items[0].row()
        
        # Get location data
        location_id = self.locations_table.item(row, 0).data(Qt.UserRole)
        location = self.db.get_location(location_id)
        
        # Center map on selected location if coordinates exist
        if location and location.lat and location.lon:
            # Center map using JavaScript
            js = f'setView({float(location.lat)}, {float(location.lon)}, 15);'
            self.map_view.page().runJavaScript(js)
    
    @Slot(str)
    def on_marker_clicked(self, location_id):
        """Handle marker click from JavaScript"""
        # Find the row with this location ID and select it
        for row in range(self.locations_table.rowCount()):
            if self.locations_table.item(row, 0).data(Qt.UserRole) == location_id:
                self.locations_table.selectRow(row)
                break
    
    @Slot(float, float)
    def on_map_clicked(self, lat, lng):
        """Handle map clicks for adding points"""
        if self.add_point_mode:
            self.add_location(lat, lng)
            self.add_point_btn.setChecked(False)
            self.add_point_mode = False
    
  
    def add_location(self, lat=None, lng=None):
        """Add a new location"""
        if not self.db:
            QMessageBox.warning(self, "Error", "No database connection")
            return
            
        if not self.project_id:
            QMessageBox.warning(self, "Error", "No project selected")
            return
        
        dialog = LocationDialog(self, db=self.db)
        if lat is not None and lng is not None:
            dialog.latitude.setText(str(lat))
            dialog.longitude.setText(str(lng))
        
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            name = data.pop('name')
            if not name:
                QMessageBox.warning(self, "Error", "Name is required")
                return
                
            success, message, location_id = self.db.create_location(self.project_id, name, **data)
            if success:
                self.update_locations()
            else:
                QMessageBox.warning(self, "Error", f"Failed to create location: {message}")
    
    def edit_location(self):
        """Edit the selected location"""
        selected_items = self.locations_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select a location to edit")
            return
            
        # Get location ID from the name cell
        row = selected_items[0].row()
        location_id = self.locations_table.item(row, 0).data(Qt.UserRole)
        if not location_id:
            QMessageBox.warning(self, "Error", "Invalid location selected")
            return
            
        # Get location from database
        location = self.db.get_location(location_id)
        if not location:
            QMessageBox.warning(self, "Error", "Location not found")
            return
            
        # Open dialog with location data
        self.current_dialog = LocationDialog(self, location=location, db=self.db)
        if self.current_dialog.exec() == QDialog.Accepted:
            data = self.current_dialog.get_data()
            name = data.pop('name')
            if not name:
                QMessageBox.warning(self, "Error", "Name is required")
                return
                
            success, message = self.db.update_location(location_id, name=name, **data)
            if success:
                self.update_locations()
            else:
                QMessageBox.warning(self, "Error", f"Failed to update location: {message}")
        
        # Clear current dialog reference
        self.current_dialog = None
    
    def delete_location(self):
        """Delete the selected location"""
        selected_items = self.locations_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select a location to delete")
            return
            
        # Get location ID from the name cell
        row = selected_items[0].row()
        location_id = self.locations_table.item(row, 0).data(Qt.UserRole)
        if not location_id:
            QMessageBox.warning(self, "Error", "Invalid location selected")
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this location?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.db.delete_location(location_id)
            if success:
                self.update_locations()
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete location: {message}")
    
    def import_locations(self):
        """Import locations from a file"""
        # TODO: Implement location import functionality
        QMessageBox.information(self, "Coming Soon", "Location import functionality coming soon!")
    
    def toggle_add_point_mode(self, checked):
        """Toggle add point mode"""
        self.add_point_mode = checked
        if checked:
            self.map_view.page().runJavaScript("setCrosshairCursor();")
        else:
            self.map_view.page().runJavaScript("resetCursor();")
    
    def on_selection_changed(self):
        """Handle location selection changes"""
        selected_items = self.locations_table.selectedItems()
        has_selection = len(selected_items) > 0
        
        # Enable/disable buttons
        self.edit_location_btn.setEnabled(has_selection)
        self.delete_location_btn.setEnabled(has_selection)
        self.move_location_btn.setEnabled(has_selection)
        
        # Update sample summary if a location is selected
        if has_selection:
            row = selected_items[0].row()
            # Get location ID from user role data
            location_id = self.locations_table.item(row, 0).data(Qt.UserRole)
            if location_id:
                self.update_sample_summary(location_id)
                
                # Center map on selected location
                location = self.db.get_location(location_id)
                if location and location.lat and location.lon:
                    js = f'setView({location.lat}, {location.lon}, 15);'
                    self.map_view.page().runJavaScript(js)
        else:
            self.sample_summary.update_samples([])
            
    def update_sample_summary(self, location_id):
        """Update the sample summary table for the selected location"""
        if not self.db:
            return
            
        session = self.db.get_session()
        try:
            # Get location with samples
            location = session.query(Location).options(
                joinedload(Location.samples)
            ).get(location_id)
            
            if location:
                self.sample_summary.update_samples(location.samples)
            else:
                self.sample_summary.update_samples([])
        finally:
            session.close()
