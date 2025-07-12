from fastapi import HTTPException, status
from app.repositories.LocationModules.locationactivepincode import LocationActivePincodeRepository
from app.schemas.LocationModules.locationactivepincode import LocationActivePincodeCreate, LocationActivePincodeUpdate

class LocationActivePincodeService:
    def __init__(self, location_active_pincode_repository: LocationActivePincodeRepository, security_key: str):
        self.location_active_pincode_repository = location_active_pincode_repository
        self.security_key = security_key

    def validate_security_key(self, provided_key: str):
        """Validate the security key for API access."""
        if provided_key != self.security_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid security key."
            )

    def get_all_active_pincodes(self, security_key: str):
        """Fetch all active pincodes."""
        self.validate_security_key(security_key)
        active_pincodes = self.location_active_pincode_repository.get_all()
        if not active_pincodes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active pincodes found in the database."
            )
        return {
            "status": "success",
            "message": "Active pincodes retrieved successfully.",
            "data": active_pincodes
        }
    def get_active_pincode_by_id(self, pincode_id: int, security_key: str):
        """Fetch an active pincode by its ID."""
        self.validate_security_key(security_key)
        active_pincode = self.location_active_pincode_repository.get_by_id(pincode_id)
        if not active_pincode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active pincode with ID {pincode_id} not found."
            )
        return {
            "status": "success",
            "message": "Active pincode retrieved successfully.",
            "data": active_pincode
        }
    def create_active_pincode(self, pincode_data: LocationActivePincodeCreate, security_key: str, added_by: int):
        """Create a new active pincode."""
        self.validate_security_key(security_key)

        # Check if a pincode with the same code already exists
        existing_pincode = self.location_active_pincode_repository.get_by_pincode(pincode_data.Pincode)
        if existing_pincode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Active pincode with code '{pincode_data.Pincode}' already exists."
            )

        # Create the new active pincode
        new_pincode = self.location_active_pincode_repository.create(pincode_data, added_by)
        # if not new_pincode:
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="Failed to create active pincode."
        #     )
        return {
            "status": "success",
            "message": "Active pincode created successfully.",
            "data": new_pincode
        }
    def update_active_pincode(self, pincode_id: int, pincode_data: LocationActivePincodeUpdate, security_key: str, modified_by: int):
        """Update an existing active pincode."""
        self.validate_security_key(security_key)

        # Check if the pincode exists
        existing_pincode = self.location_active_pincode_repository.get_by_id(pincode_id)
        if not existing_pincode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active pincode with ID {pincode_id} not found."
            )

        # Update the active pincode
        updated_pincode = self.location_active_pincode_repository.update(pincode_id, pincode_data, modified_by)
        if not updated_pincode:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update active pincode."
            )
        return {
            "status": "success",
            "message": "Active pincode updated successfully.",
            "data": updated_pincode
        }
    def delete_active_pincode(self, pincode_id: int, security_key: str, deleted_by: int):
        """Delete an active pincode."""
        self.validate_security_key(security_key)

        # Check if the pincode exists
        existing_pincode = self.location_active_pincode_repository.get_by_id(pincode_id)
        if not existing_pincode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active pincode with ID {pincode_id} not found."
            )

        # Delete the active pincode
        deleted_pincode = self.location_active_pincode_repository.delete(pincode_id, deleted_by)
        if not deleted_pincode:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete active pincode."
            )
        return {
            "status": "success",
            "message": "Active pincode deleted successfully.",
            "data": deleted_pincode
        }