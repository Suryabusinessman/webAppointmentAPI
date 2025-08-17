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

    def get_all_pincodes(self, security_key: str):
        """Fetch all pincodes (both active and inactive)."""
        self.validate_security_key(security_key)
        pincodes = self.location_active_pincode_repository.get_all()
        return {
            "status": "success",
            "message": "Pincodes retrieved successfully.",
            "data": pincodes
        }

    def get_active_pincodes(self, security_key: str):
        """Fetch all active pincodes."""
        self.validate_security_key(security_key)
        active_pincodes = self.location_active_pincode_repository.get_active_pincodes()
        return {
            "status": "success",
            "message": "Active pincodes retrieved successfully.",
            "data": active_pincodes
        }

    def get_inactive_pincodes(self, security_key: str):
        """Fetch all inactive pincodes."""
        self.validate_security_key(security_key)
        inactive_pincodes = self.location_active_pincode_repository.get_inactive_pincodes()
        return {
            "status": "success",
            "message": "Inactive pincodes retrieved successfully.",
            "data": inactive_pincodes
        }

    def get_pincode_by_id(self, pincode_id: int, security_key: str):
        """Fetch a pincode by its ID."""
        self.validate_security_key(security_key)
        pincode = self.location_active_pincode_repository.get_by_id(pincode_id)
        if not pincode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pincode with ID {pincode_id} not found."
            )
        return {
            "status": "success",
            "message": "Pincode retrieved successfully.",
            "data": pincode
        }

    def create_pincode(self, pincode_data: LocationActivePincodeCreate, security_key: str, added_by: int):
        """Create a new pincode."""
        self.validate_security_key(security_key)

        # Check if a pincode with the same code already exists
        existing_pincode = self.location_active_pincode_repository.get_by_pincode(pincode_data.pincode)
        if existing_pincode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pincode with code '{pincode_data.pincode}' already exists."
            )

        # Create the new pincode
        new_pincode = self.location_active_pincode_repository.create(pincode_data, added_by)
        return {
            "status": "success",
            "message": "Pincode created successfully.",
            "data": new_pincode
        }

    def update_pincode(self, pincode_id: int, pincode_data: LocationActivePincodeUpdate, security_key: str, modified_by: int):
        """Update an existing pincode."""
        self.validate_security_key(security_key)

        # Check if the pincode exists
        existing_pincode = self.location_active_pincode_repository.get_by_id(pincode_id)
        if not existing_pincode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pincode with ID {pincode_id} not found."
            )

        # Update the pincode
        updated_pincode = self.location_active_pincode_repository.update(pincode_id, pincode_data, modified_by)
        return {
            "status": "success",
            "message": "Pincode updated successfully.",
            "data": updated_pincode
        }

    def delete_pincode(self, pincode_id: int, security_key: str, deleted_by: int):
        """Delete a pincode."""
        self.validate_security_key(security_key)

        # Check if the pincode exists
        existing_pincode = self.location_active_pincode_repository.get_by_id(pincode_id)
        if not existing_pincode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pincode with ID {pincode_id} not found."
            )

        # Delete the pincode
        deleted_pincode = self.location_active_pincode_repository.delete(pincode_id, deleted_by)
        return {
            "status": "success",
            "message": "Pincode deleted successfully.",
            "data": deleted_pincode
        }

    def toggle_pincode_status(self, pincode_id: int, security_key: str, modified_by: int):
        """Toggle the active status of a pincode."""
        self.validate_security_key(security_key)
        
        # Check if the pincode exists
        existing_pincode = self.location_active_pincode_repository.get_by_id(pincode_id)
        if not existing_pincode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pincode with ID {pincode_id} not found."
            )

        # Toggle the pincode status
        updated_pincode = self.location_active_pincode_repository.toggle_active_status(pincode_id, modified_by)
        return {
            "status": "success",
            "message": "Pincode status toggled successfully.",
            "data": updated_pincode
        }