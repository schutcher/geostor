import sqlite3
import os

def create_geostor_database(db_path="geostor/database/geostor.db"):
    """
    Creates a SQLite database (if it doesn't already exist) in the 'database' folder
    and defines a 'project' table. Uses an auto-increment primary key for uniqueness,
    plus a project_number field for external IDs.
    """
    # Ensure the 'database' directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    create_project_table_query = '''
    CREATE TABLE IF NOT EXISTS project (
        project_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Surrogate primary key
        project_number TEXT,                            -- External project ID (possibly non-unique)
        project_name TEXT,                              -- Project title
        project_location TEXT,                          -- Location of site
        project_client TEXT,                            -- Client name
        project_contractor TEXT,                        -- Contractor's name
        project_engineer TEXT,                          -- Project Engineer
        project_comments TEXT,                          -- General project comments
        file_reference TEXT                             -- Associated file reference
    )
    '''
    cursor.execute(create_project_table_query)
    connection.commit()

    create_location_table_query = """
    CREATE TABLE IF NOT EXISTS location (
        location_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Surrogate primary key
        project_id INTEGER NOT NULL,                    -- Foreign key to 'project' table
        location_name TEXT,                             -- Location name
        location_type TEXT,                             -- Type of activity
        location_status TEXT,                           -- Status of information for this location
        location_easting REAL,                          -- National Grid Easting of location
        location_northing REAL,                         -- National Grid Northing of location
        location_epsg_code TEXT,                        -- EPSG code
        location_grid_ref_system TEXT,                  -- National grid referencing system used
        location_ground_elevation REAL,                 -- Ground level relative to datum
        location_remarks TEXT,                          -- General remarks
        location_final_depth REAL,                      -- Final depth
        location_start_date TEXT,                       -- Date activity started
        location_purpose TEXT,                          -- Purpose of activity
        location_termination_reason TEXT,               -- Reason for terminating activity
        location_end_date TEXT,                         -- Date activity ended
        location_letter_grid_ref TEXT,                  -- OSGB letter grid reference
        location_local_x REAL,                          -- Local grid X coordinate
        location_local_y REAL,                          -- Local grid Y coordinate
        location_local_z REAL,                          -- Local datum elevation
        location_local_grid_ref_system TEXT,            -- Local grid referencing system used
        location_local_datum_system TEXT,               -- Local datum referencing system used
        location_easting_end_traverse REAL,             -- Easting at end of traverse
        location_northing_end_traverse REAL,            -- Northing at end of traverse
        location_ground_level_end_traverse REAL,        -- Ground level at end of traverse
        location_local_x_end_traverse REAL,             -- Local grid X at end of traverse
        location_local_y_end_traverse REAL,             -- Local grid Y at end of traverse
        location_local_z_end_traverse REAL,             -- Local datum Z at end of traverse
        location_lat TEXT,                              -- Latitude of location/start
        location_lon TEXT,                              -- Longitude of location/start
        location_end_lat TEXT,                          -- Latitude at end of traverse
        location_end_lon TEXT,                          -- Longitude at end of traverse
        location_projection_format TEXT,                -- Projection Format
        location_method TEXT,                           -- Method of location
        location_sub_division TEXT,                     -- Site location sub-division
        location_phase_grouping_code TEXT,              -- Investigation phase grouping code
        location_alignment_id TEXT,                     -- Alignment identifier
        location_offset REAL,                           -- Offset
        location_chainage TEXT,                         -- Chainage
        location_algorithm_ref TEXT,                    -- Reference to details of algorithm
        file_reference TEXT,                            -- Associated file reference
        location_national_datum_system TEXT,            -- National Datum referencing system used
        location_original_hole_id TEXT,                 -- Original Hole ID
        location_original_job_ref TEXT,                 -- Original Job Reference
        location_originating_company TEXT,              -- Originating company
        FOREIGN KEY (project_id) REFERENCES project(project_id)
    )
    """
    cursor.execute(create_location_table_query)
    connection.commit()

    create_abbreviations_table_query = """
    CREATE TABLE IF NOT EXISTS ags_abbreviations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        abbr_heading TEXT,      -- e.g., LOCA_TYPE
        abbr_code TEXT,         -- e.g., BH
        abbr_description TEXT,  -- e.g., Borehole
        abbr_list TEXT,         -- 
        abbr_remarks TEXT,      --
        abbr_file_set TEXT      --
    )
    """
    cursor.execute(create_abbreviations_table_query)
    connection.commit()

    connection.close()
    print(f"Database created/updated successfully at '{db_path}'.")


if __name__ == "__main__":
    create_geostor_database()
