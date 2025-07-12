from fastapi import HTTPException, status
from app.repositories.LocationModules.locationmaster import LocationMasterRepository
from app.schemas.LocationModules.locationmaster import LocationMasterCreate, LocationMasterUpdate

class LocationMasterService:
    def __init__(self, location_master_repository: LocationMasterRepository, security_key: str):
        self.location_master_repository = location_master_repository
        self.security_key = security_key

    def validate_security_key(self, provided_key: str):
        """Validate the security key for API access."""
        if provided_key != self.security_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid security key."
            )

    def get_all_locations(self, security_key: str):
        """Fetch all locations."""
        self.validate_security_key(security_key)
        locations = self.location_master_repository.get_all()
        if not locations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No locations found in the database."
            )
        return {
            "status": "success",
            "message": "Locations retrieved successfully.",
            "data": locations
        }
    def get_location_by_id(self, location_id: int, security_key: str):
        """Fetch a location by its ID."""
        self.validate_security_key(security_key)
        location = self.location_master_repository.get_by_id(location_id)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID {location_id} not found."
            )
        return {
            "status": "success",
            "message": "Location retrieved successfully.",
            "data": location
        }
    def create_location(self, location_data: LocationMasterCreate, security_key: str, added_by: int):
        """Create a new location."""
        self.validate_security_key(security_key)

        # Check if a location with the same name already exists
        existing_location = self.location_master_repository.get_by_name(location_data.Location_Name)
        if existing_location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location with name '{location_data.Location_Name}' already exists."
            )

        # Create the new location
        new_location = self.location_master_repository.create(location_data, added_by)
        if not new_location:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create Location."
            )
        return {
            "status": "success",
            "message": "Location created successfully.",
            "data": new_location
        }
    def update_location(self, location_id: int, location_data: LocationMasterUpdate, security_key: str, modified_by: int):
        """Update an existing location."""
        self.validate_security_key(security_key)

        # Check if the location exists
        existing_location = self.location_master_repository.get_by_id(location_id)
        if not existing_location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID {location_id} not found."
            )

        # Update the location
        updated_location = self.location_master_repository.update(location_id, location_data, modified_by)
        if not updated_location:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update Location."
            )
        return {
            "status": "success",
            "message": "Location updated successfully.",
            "data": updated_location
        }
    def delete_location(self, location_id: int, security_key: str, deleted_by: int):    
        """Delete a location."""
        self.validate_security_key(security_key)

        # Check if the location exists
        existing_location = self.location_master_repository.get_by_id(location_id)
        if not existing_location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID {location_id} not found."
            )
        if existing_location.Is_Deleted == 'Y':    
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Business Category is already deleted."
                    )
        # Delete the location
        deleted_location = self.location_master_repository.delete(location_id, deleted_by)
        
        if not deleted_location:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete Location."
            )
        return {
            "status": "success",
            "message": "Location deleted successfully.",
            "data": deleted_location
        }
        