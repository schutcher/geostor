from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    number = Column(String, unique=True)
    location = Column(String)
    client = Column(String)
    contractor = Column(String)
    engineer = Column(String)
    memo = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    locations = relationship("Location", back_populates="project", cascade="all, delete-orphan")

class Location(Base):
    __tablename__ = 'locations'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String)
    status = Column(String)
    easting = Column(Float)
    northing = Column(Float)
    epsg_code = Column(String)
    grid_ref_system = Column(String)
    ground_elevation = Column(Float)
    remarks = Column(String)
    final_depth = Column(Float)
    start_date = Column(String)
    purpose = Column(String)
    termination_reason = Column(String)
    end_date = Column(String)
    letter_grid_ref = Column(String)
    local_x = Column(Float)
    local_y = Column(Float)
    local_z = Column(Float)
    local_grid_ref_system = Column(String)
    local_datum_system = Column(String)
    easting_end_traverse = Column(Float)
    northing_end_traverse = Column(Float)
    ground_level_end_traverse = Column(Float)
    local_x_end_traverse = Column(Float)
    local_y_end_traverse = Column(Float)
    local_z_end_traverse = Column(Float)
    lat = Column(Float)
    lon = Column(Float)
    end_lat = Column(Float)
    end_lon = Column(Float)
    projection_format = Column(String)
    method = Column(String)
    sub_division = Column(String)
    phase_grouping_code = Column(String)
    alignment_id = Column(String)
    offset = Column(Float)
    chainage = Column(String)
    algorithm_ref = Column(String)
    file_reference = Column(String)
    national_datum_system = Column(String)
    original_hole_id = Column(String)
    original_job_ref = Column(String)
    originating_company = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="locations")
    samples = relationship("Sample", back_populates="location", cascade="all, delete-orphan")
    geology = relationship("Geology", back_populates="location", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('project_id', 'name', name='uix_location_project_name'),
    )

class Sample(Base):
    __tablename__ = 'samples'
    
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id', ondelete='CASCADE'), nullable=False)
    reference = Column(String, nullable=False)
    type = Column(String)
    top_depth = Column(Float)
    bottom_depth = Column(Float)
    description = Column(String)
    remarks = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    location = relationship("Location", back_populates="samples")
    laboratory_tests = relationship("Laboratory", back_populates="sample", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('location_id', 'reference', name='uix_sample_location_reference'),
    )

class Geology(Base):
    __tablename__ = 'geology'
    
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id', ondelete='CASCADE'), nullable=False)
    top_depth = Column(Float, nullable=False)
    bottom_depth = Column(Float, nullable=False)
    legend = Column(String)
    description = Column(String)
    consistency = Column(String)
    weathering = Column(String)
    structure = Column(String)
    remarks = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    location = relationship("Location", back_populates="geology")

class Laboratory(Base):
    __tablename__ = 'laboratory'
    
    id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey('samples.id', ondelete='CASCADE'), nullable=False)
    test_type = Column(String, nullable=False)
    test_result = Column(Float)
    test_unit = Column(String)
    test_date = Column(String)
    remarks = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sample = relationship("Sample", back_populates="laboratory_tests")

class AGSAbbreviation(Base):
    __tablename__ = 'ags_abbreviations'
    
    id = Column(Integer, primary_key=True)
    abbr_heading = Column(String, nullable=False)  # e.g., "LOCA_TYPE"
    abbr_code = Column(String, nullable=False)     # e.g., "BH"
    abbr_description = Column(String)              # e.g., "Borehole"
    abbr_list = Column(String)                     # if present
    abbr_remarks = Column(String)
    abbr_file_set = Column(String)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('abbr_heading', 'abbr_code', name='uix_heading_code'),
    )

def init_database(db_path: str):
    """Initialize the database with all tables"""
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    """Create a new session factory"""
    return sessionmaker(bind=engine)
