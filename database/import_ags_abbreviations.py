import csv
import sqlite3
import os

DB_PATH = "geostor/database/geostor.db"
CSV_FILE = "geostor/database/AGS_abbreviations.csv"

def import_ags_abbreviations(db_path=DB_PATH, csv_file=CSV_FILE):
    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        return

    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON;")
    cursor = connection.cursor()

    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Adjust these field names to match CSV column headers
        for row in reader:
            abbr_heading = row.get("ABBR_HDNG")    # e.g., "LOCA_TYPE"
            abbr_code = row.get("ABBR_CODE")       # e.g., "BH"
            abbr_description = row.get("ABBR_DESC")# e.g., "Borehole"
            abbr_list = row.get("ABBR_LIST")     # if present
            abbr_remarks = row.get("ABBR_REM")
            abbr_file_set = row.get("FILE_FSET")

            # Insert row
            insert_query = """
                INSERT INTO ags_abbreviations (abbr_heading, abbr_code, abbr_description, abbr_list, abbr_remarks, abbr_file_set)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (abbr_heading, abbr_code, abbr_description, abbr_list, abbr_remarks, abbr_file_set))

    connection.commit()
    connection.close()
    print("AGS abbreviations data imported successfully.")

if __name__ == "__main__":
    import_ags_abbreviations()
