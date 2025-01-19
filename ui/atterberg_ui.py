import sys
import sqlite3
import logging
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt

from geostor.calculations.atterberg_calculations import process_atterberg_limits

class AtterbergWindow(QMainWindow):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.setWindowTitle("Atterberg Limit Input UI")

        # Setup main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Main layout
        self.main_layout = QVBoxLayout()
        main_widget.setLayout(self.main_layout)

        # -- 1. Project/Location/Sample Selection Layout  --
        self.selection_layout = QHBoxLayout()

        # Project ComboBox
        self.project_label = QLabel("Project:")
        self.project_combo = QComboBox()
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)

        # Location ComboBox
        self.location_label = QLabel("Location:")
        self.location_combo = QComboBox()
        self.location_combo.currentIndexChanged.connect(self.on_location_changed)

        # Sample ComboBox
        self.sample_label = QLabel("Sample:")
        self.sample_combo = QComboBox()

        self.selection_layout.addWidget(self.project_label)
        self.selection_layout.addWidget(self.project_combo)
        self.selection_layout.addWidget(self.location_label)
        self.selection_layout.addWidget(self.location_combo)
        self.selection_layout.addWidget(self.sample_label)
        self.selection_layout.addWidget(self.sample_combo)

        self.main_layout.addLayout(self.selection_layout)

        # Populate Project ComboBox
        self.populate_projects()

        # -- 2. Liquid Limit Table --
        self.ll_table_label = QLabel("Liquid Limit Trials:")
        self.ll_table = QTableWidget()
        self.ll_table.setColumnCount(5)
        self.ll_table.setHorizontalHeaderLabels(["Trial", "Drops", "Tare", "TareMoist", "TareDry"])
        self.ll_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ll_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        # For user convenience, we can pre-populate a few blank rows:
        self.ll_table.setRowCount(3)

        # -- 3. Plastic Limit Table --
        self.pl_table_label = QLabel("Plastic Limit Trials:")
        self.pl_table = QTableWidget()
        self.pl_table.setColumnCount(4)
        self.pl_table.setHorizontalHeaderLabels(["Trial", "Tare", "TareMoist", "TareDry"])
        self.pl_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pl_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.pl_table.setRowCount(3)

        # Put the two tables into a grid or horizontal layout
        tables_layout = QGridLayout()
        tables_layout.addWidget(self.ll_table_label, 0, 0)
        tables_layout.addWidget(self.ll_table, 1, 0)
        tables_layout.addWidget(self.pl_table_label, 0, 1)
        tables_layout.addWidget(self.pl_table, 1, 1)

        self.main_layout.addLayout(tables_layout)

        # -- 4. Buttons for Save / Calculate / Show Plot --
        self.button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save Data")
        self.save_button.clicked.connect(self.save_data)

        self.calc_button = QPushButton("Calculate / Plot")
        self.calc_button.clicked.connect(self.calculate_and_plot)

        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.calc_button)

        self.main_layout.addLayout(self.button_layout)

        # -- 5. Status/Message Label (optional) --
        self.status_label = QLabel("Status messages here...")
        self.main_layout.addWidget(self.status_label)

    # ---------------------------------------------------------------------
    # Database helper: get all projects in project table
    def populate_projects(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT project_id, project_number FROM project")
        projects = cursor.fetchall()
        conn.close()

        # Clear before populating
        self.project_combo.clear()
        self.project_combo.addItem("-- Select Project --", userData=None)

        for pid, pnum in projects:
            self.project_combo.addItem(pnum, userData=pid)

    # On changing project, populate the location combo
    def on_project_changed(self):
        # Clear location and sample combos
        self.location_combo.clear()
        self.sample_combo.clear()

        project_id = self.project_combo.currentData()
        if not project_id:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT location_id, location_name 
            FROM location
            WHERE project_id = ?
        """, (project_id,))
        locations = cursor.fetchall()
        conn.close()

        self.location_combo.addItem("-- Select Location --", userData=None)
        for lid, lname in locations:
            self.location_combo.addItem(lname, userData=lid)

    # On changing location, populate the sample combo
    def on_location_changed(self):
        self.sample_combo.clear()
        location_id = self.location_combo.currentData()
        if not location_id:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sample_id, sample_reference
            FROM sample
            WHERE location_id = ?
        """, (location_id,))
        samples = cursor.fetchall()
        conn.close()

        self.sample_combo.addItem("-- Select Sample --", userData=None)
        for sid, sref in samples:
            self.sample_combo.addItem(sref, userData=sid)

    # ---------------------------------------------------------------------
    # 1) Save data to "liquidlimit" and "plasticlimit" tables
    def save_data(self):
        # Grab the selected sample
        sample_id = self.sample_combo.currentData()
        if not sample_id:
            QMessageBox.warning(self, "Sample not selected", "Please select a valid sample!")
            return

        # Gather user-entered Liquid Limit data
        ll_rows = []
        for row_idx in range(self.ll_table.rowCount()):
            try:
                trial_item = self.ll_table.item(row_idx, 0)
                drops_item = self.ll_table.item(row_idx, 1)
                tare_item = self.ll_table.item(row_idx, 2)
                tare_moist_item = self.ll_table.item(row_idx, 3)
                tare_dry_item = self.ll_table.item(row_idx, 4)

                if not trial_item or not trial_item.text().strip():
                    continue  # skip empty row

                trial = int(trial_item.text())
                drops = float(drops_item.text())
                tare = float(tare_item.text())
                tare_moist = float(tare_moist_item.text())
                tare_dry = float(tare_dry_item.text())

                ll_rows.append((sample_id, trial, drops, tare, tare_moist, tare_dry))
            except:
                pass

        # Gather user-entered Plastic Limit data
        pl_rows = []
        for row_idx in range(self.pl_table.rowCount()):
            try:
                trial_item = self.pl_table.item(row_idx, 0)
                tare_item = self.pl_table.item(row_idx, 1)
                tare_moist_item = self.pl_table.item(row_idx, 2)
                tare_dry_item = self.pl_table.item(row_idx, 3)

                if not trial_item or not trial_item.text().strip():
                    continue  # skip empty row

                trial = int(trial_item.text())
                tare = float(tare_item.text())
                tare_moist = float(tare_moist_item.text())
                tare_dry = float(tare_dry_item.text())

                pl_rows.append((sample_id, trial, tare, tare_moist, tare_dry))
            except:
                pass

        # Insert data into the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Liquid Limit Insert
        ll_insert_sql = """
            INSERT INTO liquidlimit (sample_id, trial, drops, tare, taremoist, taredry)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        for row in ll_rows:
            cursor.execute(ll_insert_sql, row)

        # Plastic Limit Insert
        pl_insert_sql = """
            INSERT INTO plasticlimit (sample_id, trial, tare, taremoist, taredry)
            VALUES (?, ?, ?, ?, ?)
        """
        for row in pl_rows:
            cursor.execute(pl_insert_sql, row)

        conn.commit()
        conn.close()

        msg = f"Saved {len(ll_rows)} Liquid Limit trial(s) and {len(pl_rows)} Plastic Limit trial(s) to DB."
        self.status_label.setText(msg)
        QMessageBox.information(self, "Data Saved", msg)

    # ---------------------------------------------------------------------
    # 2) Calculate / Plot
    def calculate_and_plot(self):
        # The real function you wrote: process_atterberg_limits(db_file, project_number)
        # We need to pass the user-chosen project_number. Let's query that:
        project_id = self.project_combo.currentData()
        if not project_id:
            QMessageBox.warning(self, "No Project Selected", "Please select a valid project!")
            return

        # Let's find the actual project number from the DB:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT project_number FROM project WHERE project_id = ?", (project_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            QMessageBox.warning(self, "Error", "Could not find project_number for that project_id.")
            return

        project_number = row[0]

        # Now call your process_atterberg_limits function:
        try:
            process_atterberg_limits(self.db_path, project_number)
            # If your function logs or prints warnings about ASTM issues,
            # we can show them in a message box or label. For demonstration,
            # let's just show a generic "Completed" message.
            self.status_label.setText("Atterberg Calculations Completed. Check logs/plots.")
            QMessageBox.information(self, "Done", "Atterberg Calculations Completed!\nCheck generated plots.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.status_label.setText(str(e))


def main():
    app = QApplication(sys.argv)
    
    # Calculate path to database within the geostor package
    # __file__ is in geostor/ui/, need to go up one level to geostor/ then into database/
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                          "database", "geostor.db")
    
    if not os.path.exists(db_path):
        QMessageBox.critical(None, "Error", f"Database not found at: {db_path}")
        sys.exit(1)
        
    window = AtterbergWindow(db_path)
    window.resize(1200, 600)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
