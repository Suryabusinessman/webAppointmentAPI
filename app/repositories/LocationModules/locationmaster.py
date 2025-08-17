from sqlalchemy.orm import Session
from app.models.LocationModules.locationmaster import LocationMaster
from app.schemas.LocationModules.locationmaster import LocationMasterCreate, LocationMasterUpdate
from fastapi import HTTPException, status
from datetime import datetime

class LocationMasterRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        """Fetch all active locations."""
        locations = self.db.query(LocationMaster).filter(LocationMaster.is_deleted == 'N').all()
        if not locations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No locations found in the database."
            )
        return locations

    def get_active_locations(self):
        """Fetch all active locations."""
        locations = self.db.query(LocationMaster).filter(
            LocationMaster.is_deleted == 'N',
            LocationMaster.is_active == 'Y'
        ).all()
        if not locations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active locations found in the database."
            )
        return locations

    def get_inactive_locations(self):
        """Fetch all inactive locations."""
        locations = self.db.query(LocationMaster).filter(
            LocationMaster.is_deleted == 'N',
            LocationMaster.is_active == 'N'
        ).all()
        if not locations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No inactive locations found in the database."
            )
        return locations

    def toggle_active_status(self, location_id: int, modified_by: int):
        """Toggle the active status of a location."""
        location = self.get_by_id(location_id)
        if location.is_deleted == 'Y':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location with ID {location_id} is deleted and cannot be modified."
            )
        
        # Toggle the active status
        location.is_active = 'N' if location.is_active == 'Y' else 'Y'
        location.modified_by = modified_by
        location.modified_on = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(location)
        return location

    def get_by_id(self, location_id: int):
        """Fetch a location by its ID."""
        location = self.db.query(LocationMaster).filter(
            LocationMaster.location_id == location_id,
            LocationMaster.is_deleted == 'N'
        ).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID {location_id} not found."
            )
        return location
    def get_by_name(self, location_name: str):
        """Fetch a location by its name."""
        location = self.db.query(LocationMaster).filter(
            LocationMaster.location_name == location_name,
            LocationMaster.is_deleted == 'N'
        ).first()
        # if not location:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Location with name {location_name} not found."
        #     )
        return location
    def create(self, location_data: LocationMasterCreate, added_by: int):
        """Create a new location."""
        # Check if a location with the same name already exists
        existing_location = self.db.query(LocationMaster).filter(
            LocationMaster.location_name == location_data.location_name,
            LocationMaster.is_deleted == 'N'
        ).first()

        # Log a message if the location already exists
        if existing_location:
            print(f"Location with name '{location_data.location_name}' already exists. Creating a new location.")
        if existing_location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location with name '{location_data.location_name}' already exists."
            )
        # Create the new location regardless of whether the name exists
        new_location = LocationMaster(
            location_name=location_data.location_name,
            location_city_name=location_data.location_city_name,
            location_dist_name=location_data.location_dist_name,
            location_state_name=location_data.location_state_name,
            location_country_name=location_data.location_country_name,
            location_desc=location_data.location_desc,
            is_active=location_data.is_active, 
            is_deleted='N',
            added_by=added_by,
            added_on=datetime.utcnow()
        )
        self.db.add(new_location)
        self.db.commit()
        self.db.refresh(new_location)
        return new_location
    def update(self, location_id: int, location_data: LocationMasterUpdate, modified_by: int):
        """Update an existing location."""
        location = self.get_by_id(location_id)
        if location.is_deleted == 'Y':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location with ID {location_id} is deleted and cannot be updated."
            )
        if location_data.location_name:
            existing_location = self.get_by_name(location_data.location_name)
            if existing_location and existing_location.location_id != location_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Location with name '{location_data.location_name}' already exists."
                )
            location.location_name = location_data.location_name
        if location_data.location_city_name:
            location.location_city_name = location_data.location_city_name
        if location_data.location_dist_name:
            location.location_dist_name = location_data.location_dist_name
        if location_data.location_state_name:
            location.location_state_name = location_data.location_state_name
        if location_data.location_country_name:
            location.location_country_name = location_data.location_country_name
        if location_data.location_desc:
            location.location_desc = location_data.location_desc
        if location_data.is_active:
            location.is_active = location_data.is_active
        # for key, value in location_data.dict(exclude_unset=True).items():
        #     setattr(location, key, value)
        location.modified_by = modified_by
        location.modified_on = datetime.utcnow()
        self.db.commit()
        self.db.refresh(location)
        return location
    def delete(self, location_id: int, deleted_by: int):
        """Delete a location."""
        location = self.get_by_id(location_id)
        if location.is_deleted == 'Y':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location with ID {location_id} is already deleted."
            )
        location.is_deleted = 'Y'
        location.deleted_by = deleted_by
        location.deleted_on = datetime.utcnow()
        self.db.commit()
        return {"detail": f"Location with ID {location_id} has been deleted."}