from fastapi import HTTPException, status
from app.schemas.LocationModules.locationuseraddress import LocationUserAddressCreate, LocationUserAddressUpdate
from app.repositories.LocationModules.locationuseraddress import LocationUserAddressRepository

class LocationUserAddressService:
    def __init__(self, location_user_address_repository: LocationUserAddressRepository, security_key: str):
        self.location_user_address_repository = location_user_address_repository
        self.security_key = security_key

    def validate_security_key(self, provided_key: str):
        """Validate the security key for API access."""
        if provided_key != self.security_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid security key."
            )

    def get_all_user_addresses(self, security_key: str):
        """Fetch all user addresses."""
        self.validate_security_key(security_key)
        addresses = self.location_user_address_repository.get_all()
        return {
            "status": "success",
            "message": "User addresses retrieved successfully.",
            "data": addresses
        }

    def get_user_address_by_id(self, address_id: int, security_key: str):
        """Fetch a user address by its ID."""
        self.validate_security_key(security_key)
        address = self.location_user_address_repository.get_by_id(address_id)
        return {
            "status": "success",
            "message": "User address retrieved successfully.",
            "data": address
        }

    def create_user_address(self, address_data: LocationUserAddressCreate, security_key: str, added_by: int = None):
        """Create a new user address."""
        self.validate_security_key(security_key)

        # Check if a user address with the same address line already exists
        existing_address = self.location_user_address_repository.get_by_address(address_data.address_line1)
        if existing_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User address with address line '{address_data.address_line1}' already exists."
            )

        # If added_by is not provided, use the user_id from the address data
        if added_by is None:
            added_by = address_data.user_id

        # Create the new user address
        new_address = self.location_user_address_repository.create(address_data, added_by)
        return {
            "status": "success",
            "message": "User address created successfully.",
            "data": new_address
        }

    def update_user_address(self, address_id: int, address_data: LocationUserAddressUpdate, security_key: str, modified_by: int):
        """Update an existing user address."""
        self.validate_security_key(security_key)

        # Update the user address
        updated_address = self.location_user_address_repository.update(address_id, address_data, modified_by)
        return {
            "status": "success",
            "message": "User address updated successfully.",
            "data": updated_address
        }

    def delete_user_address(self, address_id: int, security_key: str, deleted_by: int):
        """Delete a user address."""
        self.validate_security_key(security_key)

        # Delete the user address
        deleted_address = self.location_user_address_repository.delete(address_id, deleted_by)
        return {
            "status": "success",
            "message": "User address deleted successfully.",
            "data": deleted_address
        }

    def get_active_user_addresses(self, security_key: str):
        """Fetch all active user addresses."""
        self.validate_security_key(security_key)
        addresses = self.location_user_address_repository.get_active_addresses()
        return {
            "status": "success",
            "message": "Active user addresses retrieved successfully.",
            "data": addresses
        }

    def get_inactive_user_addresses(self, security_key: str):
        """Fetch all inactive user addresses."""
        self.validate_security_key(security_key)
        addresses = self.location_user_address_repository.get_inactive_addresses()
        return {
            "status": "success",
            "message": "Inactive user addresses retrieved successfully.",
            "data": addresses
        }

    def get_user_addresses_by_user_id(self, user_id: int, security_key: str):
        """Fetch all addresses for a specific user."""
        self.validate_security_key(security_key)
        addresses = self.location_user_address_repository.get_by_user_id(user_id)
        return {
            "status": "success",
            "message": f"User addresses for user ID {user_id} retrieved successfully.",
            "data": addresses
        }

    def toggle_user_address_active_status(self, address_id: int, security_key: str, modified_by: int):
        """Toggle the active status of a user address."""
        self.validate_security_key(security_key)
        address = self.location_user_address_repository.toggle_active_status(address_id, modified_by)
        return {
            "status": "success",
            "message": "User address active status toggled successfully.",
            "data": address
        }

    def toggle_user_address_default_status(self, address_id: int, security_key: str, modified_by: int):
        """Toggle the default status of a user address."""
        self.validate_security_key(security_key)
        address = self.location_user_address_repository.toggle_default_status(address_id, modified_by)
        return {
            "status": "success",
            "message": "User address default status toggled successfully.",
            "data": address
        }