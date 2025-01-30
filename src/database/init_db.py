import os
import csv
from pathlib import Path
from typing import Optional, Tuple
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, AGSAbbreviation, Location, Project, Sample, Geology, Laboratory

def import_ags_abbreviations(session, csv_file: Path) -> Tuple[bool, str]:
    """Import AGS abbreviations from CSV file"""
    try:
        if not csv_file.exists():
            return False, f"CSV file not found: {csv_file}"

        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                abbr = AGSAbbreviation(
                    abbr_heading=row.get("ABBR_HDNG"),
                    abbr_code=row.get("ABBR_CODE"),
                    abbr_description=row.get("ABBR_DESC"),
                    abbr_list=row.get("ABBR_LIST"),
                    abbr_remarks=row.get("ABBR_REM"),
                    abbr_file_set=row.get("FILE_FSET")
                )
                session.add(abbr)
        
        session.commit()
        return True, "AGS abbreviations imported successfully"
    
    except Exception as e:
        session.rollback()
        return False, f"Error importing AGS abbreviations: {str(e)}"

def create_tables(engine):
    """Create all database tables"""
    # Drop existing tables
    Location.__table__.drop(engine, checkfirst=True)
    Project.__table__.drop(engine, checkfirst=True)
    Sample.__table__.drop(engine, checkfirst=True)
    Geology.__table__.drop(engine, checkfirst=True)
    Laboratory.__table__.drop(engine, checkfirst=True)
    AGSAbbreviation.__table__.drop(engine, checkfirst=True)
    
    # Create all tables
    Base.metadata.create_all(engine)

def initialize_database(db_path: Path, ags_csv_path: Optional[Path] = None) -> Tuple[bool, str]:
    """Initialize a new database with all required tables and AGS abbreviations"""
    try:
        # Create database engine
        engine = create_engine(f'sqlite:///{db_path}')
        
        # Create all tables
        create_tables(engine)
        
        # If AGS CSV file is provided, import abbreviations
        if ags_csv_path and ags_csv_path.exists():
            Session = sessionmaker(bind=engine)
            session = Session()
            
            success, message = import_ags_abbreviations(session, ags_csv_path)
            session.close()
            
            if not success:
                return False, message
        
        return True, "Database initialized successfully"
    
    except Exception as e:
        return False, f"Error initializing database: {str(e)}"
