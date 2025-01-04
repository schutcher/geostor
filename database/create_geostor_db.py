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
        project_id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Surrogate primary key
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
    connection.close()
    print(f"Database and table 'project' created successfully at '{db_path}'.")


if __name__ == "__main__":
    create_geostor_database()
