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
        if not addresses:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user addresses found in the database."
            )
        return {
            "status": "success",
            "message": "User addresses retrieved successfully.",
            "data": addresses
        }
    def get_user_address_by_id(self, address_id: int, security_key: str):
        """Fetch a user address by its ID."""
        self.validate_security_key(security_key)
        address = self.location_user_address_repository.get_by_id(address_id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User address with ID {address_id} not found."
            )
        return {
            "status": "success",
            "message": "User address retrieved successfully.",
            "data": address
        }
    def create_user_address(self, address_data: LocationUserAddressCreate, security_key: str, added_by: int):
        """Create a new user address."""
        self.validate_security_key(security_key)

        # Check if a user address with the same address line already exists
        existing_address = self.location_user_address_repository.get_by_address(address_data.Address_Line1)
        if existing_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User address with address line '{address_data.Address_Line1}' already exists."
            )

        # Create the new user address
        new_address = self.location_user_address_repository.create(address_data, added_by)
        if not new_address:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user address."
            )
        return {
            "status": "success",
            "message": "User address created successfully.",
            "data": new_address
        }
    def update_user_address(self, address_id: int, address_data: LocationUserAddressUpdate, security_key: str, modified_by: int):
        """Update an existing user address."""
        self.validate_security_key(security_key)

        # Check if the user address exists
        existing_address = self.location_user_address_repository.get_by_id(address_id)
        if not existing_address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User address with ID {address_id} not found."
            )

        # Update the user address
        updated_address = self.location_user_address_repository.update(address_id, address_data, modified_by)
        if not updated_address:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user address."
            )
        return {
            "status": "success",
            "message": "User address updated successfully.",
            "data": updated_address
        }
    def delete_user_address(self, address_id: int, security_key: str, deleted_by: int):
        """Delete a user address."""
        self.validate_security_key(security_key)

        # Check if the user address exists
        existing_address = self.location_user_address_repository.get_by_id(address_id)
        if not existing_address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User address with ID {address_id} not found."
            )

        # Delete the user address
        deleted_address = self.location_user_address_repository.delete(address_id, deleted_by)
        if not deleted_address:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user address."
            )
        return {
            "status": "success",
            "message": "User address deleted successfully.",
            "data": deleted_address
        }