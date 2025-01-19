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

    # Enable foreign keys if not already enabled
    connection.execute("PRAGMA foreign_keys = ON;")    

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

    create_sample_table_query = """
    CREATE TABLE IF NOT EXISTS sample (
        sample_id INTEGER PRIMARY KEY AUTOINCREMENT,    -- Unique sample identifier
        location_id INTEGER NOT NULL,                   -- Foreign key referencing 'location' table
        sample_top_depth REAL NOT NULL,                 -- Depth to top of sample (required)
        sample_reference TEXT NOT NULL,                 -- Sample reference (required)
        sample_type TEXT NOT NULL,                      -- Sample type (required)
        sample_base_depth REAL,                         -- Depth to base of sample
        sample_date_time TEXT,                          -- Date and time sample taken
        sample_blows INTEGER,                           -- Number of blows to drive sampler (SAMP_UBLO)
        sample_container TEXT,                          -- Sample container
        sample_preparation TEXT,                        -- Details of sample preparation at time of sampling
        sample_diameter REAL,                           -- Sample diameter
        sample_water_depth REAL,                        -- Depth to water at time of sampling
        sample_recovery_percent REAL,                   -- Percentage of sample recovered
        sample_method TEXT,                             -- Sampling technique/method (SAMP_TECH)
        sample_matrix TEXT,                             -- Sample matrix
        sample_qa_type TEXT,                            -- Sample QA type (SAMP_TYPC)
        sample_collector TEXT,                          -- Sampler's initials or name (SAMP_WHO)
        sample_reason TEXT,                             -- Reason for sampling (SAMP_WHY)
        sample_remarks TEXT,                            -- Sample remarks
        sample_description TEXT,                        -- Sample/specimen description
        sample_description_date TEXT,                   -- Date sample described
        sample_logger TEXT,                             -- Person responsible for sample description
        sample_condition TEXT,                          -- Condition/representativeness of sample
        sample_classification TEXT,                     -- Classification per EN ISO 14688-1
        sample_barometric_pressure REAL,                -- Barometric pressure at time of sampling
        sample_temperature REAL,                        -- Sample temperature at time of sampling
        sample_gas_pressure REAL,                       -- Gas pressure (above barometric)
        sample_gas_flow_rate REAL,                      -- Gas flow rate
        sample_end_date_time TEXT,                      -- Date/time sampling completed
        sample_duration TEXT,                           -- Sampling duration
        sample_caption TEXT,                            -- Caption used to describe sample
        sample_record_link TEXT,                        -- Sample record link
        sample_stratum_reference TEXT,                  -- Stratum reference (GEOL_STAT)
        file_reference TEXT,                            -- Associated file reference
        sample_recovery_length REAL,                    -- Length of sample recovered

        FOREIGN KEY (location_id) REFERENCES location(location_id)
    )
    """

    cursor.execute(create_sample_table_query)
    connection.commit()   

        # Create Liquid Limit Raw Data Table
    create_liquid_limit_table = """
    CREATE TABLE IF NOT EXISTS liquidlimit (
        ll_id INTEGER PRIMARY KEY AUTOINCREMENT,      -- Surrogate primary key
        sample_id INTEGER NOT NULL,                   -- Foreign key to 'sample' table
        trial INTEGER NOT NULL,                       -- Trial number
        drops REAL NOT NULL,                          -- Number of drops
        tare REAL NOT NULL,                           -- Tare weight
        taremoist REAL NOT NULL,                      -- Moist weight with tare
        taredry REAL NOT NULL,                        -- Dry weight with tare
        is_active INTEGER DEFAULT 1,                 -- Flag for active/inactive data
        FOREIGN KEY (sample_id) REFERENCES sample(sample_id)
    )
    """
    cursor.execute(create_liquid_limit_table)
    connection.commit()

    # Create Plastic Limit Raw Data Table
    create_plastic_limit_table = """
    CREATE TABLE IF NOT EXISTS plasticlimit (
        pl_id INTEGER PRIMARY KEY AUTOINCREMENT,      -- Surrogate primary key
        sample_id INTEGER NOT NULL,                   -- Foreign key to 'sample' table
        trial INTEGER NOT NULL,                       -- Trial number
        tare REAL NOT NULL,                           -- Tare weight
        taremoist REAL NOT NULL,                      -- Moist weight with tare
        taredry REAL NOT NULL,                        -- Dry weight with tare
        is_active INTEGER DEFAULT 1,                 -- Flag for active/inactive data
        FOREIGN KEY (sample_id) REFERENCES sample(sample_id)
    )
    """
    cursor.execute(create_plastic_limit_table)
    connection.commit()

    # Create Atterberg Limits Final Values Table
    create_atterberg_limits_table = """
    CREATE TABLE IF NOT EXISTS atterberglimits (
        atterberg_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Surrogate primary key
        sample_id INTEGER NOT NULL,                     -- Foreign key to 'sample' table
        liquid_limit REAL,                               -- Calculated Liquid Limit
        plastic_limit REAL,                              -- Calculated Plastic Limit
        plasticity_index REAL,                           -- Calculated Plasticity Index
        soil_description TEXT DEFAULT 'NP',             -- Soil description (default NP)
        date_calculated TEXT DEFAULT CURRENT_TIMESTAMP, -- Timestamp of calculation
        is_active INTEGER DEFAULT 1,                    -- Flag for active/inactive data
        FOREIGN KEY (sample_id) REFERENCES sample(sample_id)
    )
    """
    cursor.execute(create_atterberg_limits_table)
    connection.commit()
 

    connection.close()
    print(f"Database created/updated successfully at '{db_path}'.")


if __name__ == "__main__":
    create_geostor_database()
