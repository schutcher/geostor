from pathlib import Path
from typing import List, Optional, Tuple, Dict
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from .models import (
    init_database, get_session, Project, Location, Sample,
    Geology, Laboratory, AGSAbbreviation
)

class DatabaseOperations:
    def __init__(self, db_path: str):
        self.engine = init_database(db_path)
        self.Session = get_session(self.engine)
    
    def get_session(self):
        """Get a new session"""
        return self.Session()
    
    def close(self):
        """Close the database session"""
        self.Session.close_all()
    
    # Project operations
    def create_project(self, name: str, **kwargs) -> Tuple[bool, str, Optional[int]]:
        """Create a new project"""
        session = self.get_session()
        try:
            project = Project(name=name, **kwargs)
            session.add(project)
            session.commit()
            # Get the ID and refresh the object to ensure all attributes are loaded
            project_id = project.id
            session.refresh(project)
            # Expunge the object from the session so it can be used after session close
            session.expunge(project)
            session.close()
            return True, "Project created successfully", project_id
        except IntegrityError:
            session.rollback()
            session.close()
            return False, f"Project with name '{name}' already exists", None
        except Exception as e:
            session.rollback()
            session.close()
            return False, f"Error creating project: {str(e)}", None
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Get a project by ID"""
        session = self.get_session()
        try:
            project = session.query(Project).get(project_id)
            session.close()
            return project
        except Exception as e:
            print(f"Error getting project: {str(e)}")
            session.close()
            return None
    
    def get_all_projects(self) -> List[Project]:
        """Get all projects"""
        session = self.get_session()
        try:
            projects = session.query(Project).order_by(Project.name).all()
            session.close()
            return projects
        except Exception as e:
            print(f"Error getting projects: {str(e)}")
            session.close()
            return []
    
    def search_projects(self, search_text: str) -> List[Project]:
        """Search projects by name or number"""
        session = self.get_session()
        try:
            projects = session.query(Project).filter(
                or_(
                    Project.name.ilike(f"%{search_text}%"),
                    Project.number.ilike(f"%{search_text}%")
                )
            ).order_by(Project.name).all()
            session.close()
            return projects
        except Exception as e:
            print(f"Error searching projects: {str(e)}")
            session.close()
            return []
    
    def update_project(self, project_id: int, **kwargs) -> Tuple[bool, str]:
        """Update an existing project"""
        session = self.get_session()
        try:
            project = session.query(Project).get(project_id)
            if not project:
                session.close()
                return False, f"Project with ID {project_id} not found"
            
            # Update project fields
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            session.commit()
            session.close()
            return True, "Project updated successfully"
        except IntegrityError:
            session.rollback()
            session.close()
            return False, "A project with this name already exists"
        except Exception as e:
            session.rollback()
            session.close()
            return False, f"Error updating project: {str(e)}"
    
    # Location operations
    def create_location(self, project_id: int, name: str, **kwargs) -> Tuple[bool, str, Optional[int]]:
        """Create a new location"""
        session = self.get_session()
        try:
            location = Location(project_id=project_id, name=name, **kwargs)
            session.add(location)
            session.commit()
            # Get the ID and refresh the object to ensure all attributes are loaded
            location_id = location.id
            session.refresh(location)
            # Expunge the object from the session so it can be used after session close
            session.expunge(location)
            session.close()
            return True, "Location created successfully", location_id
        except IntegrityError:
            session.rollback()
            session.close()
            return False, f"Location with name '{name}' already exists in this project", None
        except Exception as e:
            session.rollback()
            session.close()
            return False, f"Error creating location: {str(e)}", None
    
    def get_project_locations(self, project_id: int) -> List[Location]:
        """Get all locations for a project"""
        session = self.get_session()
        try:
            locations = session.query(Location).filter_by(project_id=project_id).order_by(Location.name).all()
            session.close()
            return locations
        except Exception as e:
            print(f"Error getting locations: {str(e)}")
            session.close()
            return []
    
    def get_locations(self, project_id: int = None) -> List[Location]:
        """Get all locations for a project"""
        session = self.get_session()
        try:
            query = session.query(Location)
            if project_id:
                query = query.filter_by(project_id=project_id)
            locations = query.order_by(Location.name).all()
            session.close()
            return locations
        except Exception as e:
            print(f"Error getting locations: {str(e)}")
            session.close()
            return []
    
    def get_location(self, location_id: int) -> Optional[Location]:
        """Get a specific location by ID"""
        session = self.get_session()
        try:
            location = session.query(Location).get(location_id)
            session.close()
            return location
        except Exception as e:
            print(f"Error getting location: {str(e)}")
            session.close()
            return None
    
    def update_location(self, location_id: int, **kwargs) -> Tuple[bool, str]:
        """Update an existing location"""
        session = self.get_session()
        try:
            location = session.query(Location).get(location_id)
            if not location:
                session.close()
                return False, f"Location with ID {location_id} not found"
            
            # Update location fields
            for key, value in kwargs.items():
                if hasattr(location, key):
                    setattr(location, key, value)
            
            # Commit changes
            session.commit()
            
            # Refresh the object to ensure it's up to date
            session.refresh(location)
            session.expunge_all()
            session.close()
            return True, "Location updated successfully"
        except Exception as e:
            session.rollback()
            session.close()
            return False, f"Error updating location: {str(e)}"
    
    def delete_location(self, location_id: int) -> Tuple[bool, str]:
        """Delete a location"""
        session = self.get_session()
        try:
            location = session.query(Location).get(location_id)
            if not location:
                session.close()
                return False, f"Location with ID {location_id} not found"
            
            session.delete(location)
            session.commit()
            session.close()
            return True, "Location deleted successfully"
        except Exception as e:
            session.rollback()
            session.close()
            return False, f"Error deleting location: {str(e)}"
    
    # Sample operations
    def create_sample(self, location_id: int, reference: str, **kwargs) -> Tuple[bool, str, Optional[int]]:
        """Create a new sample"""
        session = self.get_session()
        try:
            sample = Sample(location_id=location_id, reference=reference, **kwargs)
            session.add(sample)
            session.commit()
            session.close()
            return True, "Sample created successfully", sample.id
        except IntegrityError:
            session.rollback()
            session.close()
            return False, f"Sample with reference '{reference}' already exists for this location", None
        except Exception as e:
            session.rollback()
            session.close()
            return False, f"Error creating sample: {str(e)}", None
    
    def get_location_samples(self, location_id: int) -> List[Sample]:
        """Get all samples for a location"""
        session = self.get_session()
        try:
            samples = session.query(Sample).filter_by(location_id=location_id).order_by(Sample.top_depth).all()
            session.close()
            return samples
        except Exception as e:
            print(f"Error getting samples: {str(e)}")
            session.close()
            return []
    
    def get_sample(self, sample_id: int) -> Optional[Sample]:
        """Get a sample by ID"""
        session = self.get_session()
        try:
            sample = session.query(Sample).get(sample_id)
            if sample:
                session.refresh(sample)
            session.expunge_all()
            session.close()
            return sample
        except Exception as e:
            print(f"Error getting sample: {str(e)}")
            session.close()
            return None
    
    def update_sample(self, sample_id: int, **kwargs) -> Tuple[bool, str]:
        """Update an existing sample"""
        session = self.get_session()
        try:
            sample = session.query(Sample).get(sample_id)
            if not sample:
                session.close()
                return False, f"Sample with ID {sample_id} not found"
            
            # Update sample fields
            for key, value in kwargs.items():
                if hasattr(sample, key):
                    setattr(sample, key, value)
            
            session.commit()
            session.close()
            return True, "Sample updated successfully"
        except Exception as e:
            session.rollback()
            session.close()
            return False, f"Error updating sample: {str(e)}"
    
    def delete_sample(self, sample_id: int) -> Tuple[bool, str]:
        """Delete a sample"""
        session = self.get_session()
        try:
            sample = session.query(Sample).get(sample_id)
            if not sample:
                session.close()
                return False, f"Sample with ID {sample_id} not found"
            
            session.delete(sample)
            session.commit()
            session.close()
            return True, "Sample deleted successfully"
        except Exception as e:
            session.rollback()
            session.close()
            return False, f"Error deleting sample: {str(e)}"
    
    # Geology operations
    def create_geology(self, location_id: int, top_depth: float, bottom_depth: float, **kwargs) -> Tuple[bool, str, Optional[int]]:
        """Create a new geology record"""
        session = self.get_session()
        try:
            geology = Geology(
                location_id=location_id,
                top_depth=top_depth,
                bottom_depth=bottom_depth,
                **kwargs
            )
            session.add(geology)
            session.commit()
            session.close()
            return True, "Geology record created successfully", geology.id
        except Exception as e:
            session.rollback()
            session.close()
            return False, f"Error creating geology record: {str(e)}", None
    
    def get_location_geology(self, location_id: int) -> List[Geology]:
        """Get all geology records for a location"""
        session = self.get_session()
        try:
            geology = session.query(Geology).filter_by(location_id=location_id).order_by(Geology.top_depth).all()
            session.close()
            return geology
        except Exception as e:
            print(f"Error getting geology records: {str(e)}")
            session.close()
            return []
    
    # Laboratory operations
    def create_laboratory_test(self, sample_id: int, test_type: str, **kwargs) -> Tuple[bool, str, Optional[int]]:
        """Create a new laboratory test record"""
        session = self.get_session()
        try:
            test = Laboratory(sample_id=sample_id, test_type=test_type, **kwargs)
            session.add(test)
            session.commit()
            session.close()
            return True, "Laboratory test created successfully", test.id
        except Exception as e:
            session.rollback()
            session.close()
            return False, f"Error creating laboratory test: {str(e)}", None
    
    def get_sample_tests(self, sample_id: int) -> List[Laboratory]:
        """Get all laboratory tests for a sample"""
        session = self.get_session()
        try:
            tests = session.query(Laboratory).filter_by(sample_id=sample_id).order_by(Laboratory.test_type).all()
            session.close()
            return tests
        except Exception as e:
            print(f"Error getting laboratory tests: {str(e)}")
            session.close()
            return []
    
    # AGS Abbreviation operations
    def get_ags_codes(self, heading: str) -> List[AGSAbbreviation]:
        """Get all AGS codes for a specific heading"""
        session = self.get_session()
        try:
            codes = session.query(AGSAbbreviation)\
                .filter_by(abbr_heading=heading)\
                .order_by(AGSAbbreviation.abbr_code)\
                .all()
            session.close()
            return codes
        except Exception as e:
            print(f"Error getting AGS codes: {str(e)}")
            session.close()
            return []
    
    def get_ags_code_description(self, heading: str, code: str) -> Optional[str]:
        """Get description for a specific AGS code"""
        session = self.get_session()
        try:
            abbr = session.query(AGSAbbreviation)\
                .filter_by(abbr_heading=heading, abbr_code=code)\
                .first()
            session.close()
            return abbr.abbr_description if abbr else None
        except Exception as e:
            print(f"Error getting AGS code description: {str(e)}")
            session.close()
            return None
    
    def get_ags_codes_dict(self, heading: str) -> Dict[str, str]:
        """Get a dictionary of code:description pairs for a heading"""
        session = self.get_session()
        try:
            codes = session.query(AGSAbbreviation)\
                .filter_by(abbr_heading=heading)\
                .order_by(AGSAbbreviation.abbr_code)\
                .all()
            session.close()
            return {code.abbr_code: code.abbr_description for code in codes}
        except Exception as e:
            print(f"Error getting AGS codes dictionary: {str(e)}")
            session.close()
            return {}
    
    def get_ags_abbreviations(self, heading: str) -> List[AGSAbbreviation]:
        """Get AGS abbreviations for a specific heading"""
        session = self.get_session()
        try:
            abbreviations = session.query(AGSAbbreviation).filter_by(abbr_heading=heading).order_by(AGSAbbreviation.abbr_code).all()
            session.close()
            return abbreviations
        except Exception as e:
            print(f"Error getting AGS abbreviations: {str(e)}")
            session.close()
            return []
