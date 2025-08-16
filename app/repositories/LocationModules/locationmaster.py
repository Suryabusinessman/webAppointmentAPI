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
        locations = self.db.query(LocationMaster).filter(LocationMaster.Is_Deleted == 'N').all()
        if not locations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No locations found in the database."
            )
        return locations

    def get_by_id(self, location_id: int):
        """Fetch a location by its ID."""
        location = self.db.query(LocationMaster).filter(
            LocationMaster.Location_Id == location_id,
            LocationMaster.Is_Deleted == 'N'
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
            LocationMaster.Location_Name == location_name,
            LocationMaster.Is_Deleted == 'N'
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
            LocationMaster.Location_Name == location_data.Location_Name,
            LocationMaster.Is_Deleted == 'N'
        ).first()

        # Log a message if the location already exists
        if existing_location:
            print(f"Location with name '{location_data.Location_Name}' already exists. Creating a new location.")
        if existing_location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location with name '{location_data.Location_Name}' already exists."
            )
        # Create the new location regardless of whether the name exists
        new_location = LocationMaster(
            Location_Name=location_data.Location_Name,
            Location_City_Name=location_data.Location_City_Name,
            Location_Dist_Name=location_data.Location_Dist_Name,
            Location_State_Name=location_data.Location_State_Name,
            Location_Country_Name=location_data.Location_Country_Name,
            Location_Desc=location_data.Location_Desc,
            Is_Active=location_data.Is_Active, 
            Is_Deleted='N',
            Added_By=added_by,
            Added_On=datetime.utcnow()
        )
        self.db.add(new_location)
        self.db.commit()
        self.db.refresh(new_location)
        return new_location
    def update(self, location_id: int, location_data: LocationMasterUpdate, modified_by: int):
        """Update an existing location."""
        location = self.get_by_id(location_id)
        if location.Is_Deleted == 'Y':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location with ID {location_id} is deleted and cannot be updated."
            )
        if location_data.Location_Name:
            existing_location = self.get_by_name(location_data.Location_Name)
            if existing_location and existing_location.Location_Id != location_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Location with name '{location_data.Location_Name}' already exists."
                )
            location.Location_Name = location_data.Location_Name
        if location_data.Location_City_Name:
            location.Location_City_Name = location_data.Location_City_Name
        if location_data.Location_Dist_Name:
            location.Location_Dist_Name = location_data.Location_Dist_Name
        if location_data.Location_State_Name:
            location.Location_State_Name = location_data.Location_State_Name
        if location_data.Location_Country_Name:
            location.Location_Country_Name = location_data.Location_Country_Name
        if location_data.Location_Desc:
            location.Location_Desc = location_data.Location_Desc
        if location_data.Is_Active:
            location.Is_Active = location_data.Is_Active
        # for key, value in location_data.dict(exclude_unset=True).items():
        #     setattr(location, key, value)
        location.Modified_By = modified_by
        location.Modified_On = datetime.utcnow()
        self.db.commit()
        self.db.refresh(location)
        return location
    def delete(self, location_id: int, deleted_by: int):
        """Delete a location."""
        location = self.get_by_id(location_id)
        if location.Is_Deleted == 'Y':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location with ID {location_id} is already deleted."
            )
        location.Is_Deleted = 'Y'
        location.Deleted_By = deleted_by
        location.Deleted_On = datetime.utcnow()
        self.db.commit()
        return {"detail": f"Location with ID {location_id} has been deleted."}