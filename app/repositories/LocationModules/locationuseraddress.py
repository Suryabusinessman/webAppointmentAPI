from sqlalchemy.orm import Session
from app.models.LocationModules.locationuseraddress import LocationUserAddress
from app.models.LocationModules.locationmaster import LocationMaster
from app.models.LocationModules.locationactivepincode import LocationActivePincode
from app.models.UserModules.users import User
from app.schemas.LocationModules.locationuseraddress import LocationUserAddressCreate, LocationUserAddressUpdate
from fastapi import HTTPException, status
from datetime import datetime


class LocationUserAddressRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        """Fetch all active user addresses with related information."""
        addresses = self.db.query(
            LocationUserAddress,
            User.full_name,
            LocationMaster.location_name,
            LocationActivePincode.pincode.label('pincode_value')
        ).join(
            User, LocationUserAddress.user_id == User.user_id
        ).join(
            LocationMaster, LocationUserAddress.location_id == LocationMaster.location_id
        ).join(
            LocationActivePincode, LocationUserAddress.pincode_id == LocationActivePincode.pincode_id
        ).filter(
            LocationUserAddress.is_deleted == 'N'
        ).all()
        
        if not addresses:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user addresses found in the database."
            )
        
        # Convert to list of dictionaries with related information
        result = []
        for address, user_name, location_name, pincode_value in addresses:
            address_dict = {
                "user_address_id": address.user_address_id,
                "user_id": address.user_id,
                "location_id": address.location_id,
                "pincode_id": address.pincode_id,
                "address_line1": address.address_line1,
                "address_line2": address.address_line2,
                "city": address.city,
                "pincode": address.pincode,
                "longitude": address.longitude,
                "latitude": address.latitude,
                "map_location_url": address.map_location_url,
                "address_type": address.address_type,
                "is_default": address.is_default,
                "is_active": address.is_active,
                "added_by": address.added_by,
                "added_on": address.added_on,
                "modified_by": address.modified_by,
                "modified_on": address.modified_on,
                "deleted_by": address.deleted_by,
                "deleted_on": address.deleted_on,
                "is_deleted": address.is_deleted,
                "user_name": user_name,
                "location_name": location_name,
                "pincode_value": pincode_value
            }
            result.append(address_dict)
        
        return result

    def get_by_id(self, address_id: int):
        """Fetch a user address by its ID with related information."""
        address = self.db.query(
            LocationUserAddress,
            User.full_name,
            LocationMaster.location_name,
            LocationActivePincode.pincode.label('pincode_value')
        ).join(
            User, LocationUserAddress.user_id == User.user_id
        ).join(
            LocationMaster, LocationUserAddress.location_id == LocationMaster.location_id
        ).join(
            LocationActivePincode, LocationUserAddress.pincode_id == LocationActivePincode.pincode_id
        ).filter(
            LocationUserAddress.user_address_id == address_id,
            LocationUserAddress.is_deleted == 'N'
        ).first()
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User address with ID {address_id} not found."
            )
        
        address_obj, user_name, location_name, pincode_value = address
        
        # Add related information to the address object
        address_obj.user_name = user_name
        address_obj.location_name = location_name
        address_obj.pincode_value = pincode_value
        
        return address_obj

    def get_by_address(self, address_line: str):
        """Fetch a user address by its address line."""
        address = self.db.query(LocationUserAddress).filter(
            LocationUserAddress.address_line1 == address_line,
            LocationUserAddress.is_deleted == 'N'
        ).first()
        return address

    def create(self, address_data: LocationUserAddressCreate, added_by: int):
        """Create a new user address."""
        # Check if a user address with the same address line already exists
        existing_address = self.db.query(LocationUserAddress).filter(
            LocationUserAddress.address_line1 == address_data.address_line1,
            LocationUserAddress.is_deleted == 'N'
        ).first()

        if existing_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User address with address line '{address_data.address_line1}' already exists."
            )
        
        new_address = LocationUserAddress(
            user_id=address_data.user_id,
            location_id=address_data.location_id,
            pincode_id=address_data.pincode_id,
            address_line1=address_data.address_line1,
            address_line2=address_data.address_line2,
            city=address_data.city,
            pincode=address_data.pincode,
            longitude=address_data.longitude,
            latitude=address_data.latitude,
            map_location_url=address_data.map_location_url,
            address_type=address_data.address_type,
            is_default=address_data.is_default,
            is_active=address_data.is_active,
            added_by=added_by,
            added_on=datetime.utcnow(),
            is_deleted='N'
        )
        self.db.add(new_address)
        self.db.commit()
        self.db.refresh(new_address)
        return new_address

    def update(self, address_id: int, address_data: LocationUserAddressUpdate, modified_by: int):
        """Update an existing user address."""
        address = self.db.query(LocationUserAddress).filter(
            LocationUserAddress.user_address_id == address_id,
            LocationUserAddress.is_deleted == 'N'
        ).first()
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User address with ID {address_id} not found."
            )
        
        # Check for duplicate address line if updating
        if address_data.address_line1:
            existing_address = self.get_by_address(address_data.address_line1)
            if existing_address and existing_address.user_address_id != address_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User address with address line '{address_data.address_line1}' already exists."
                )
            address.address_line1 = address_data.address_line1
        
        # Update other fields if provided
        if address_data.address_line2 is not None:
            address.address_line2 = address_data.address_line2
        if address_data.city is not None:
            address.city = address_data.city
        if address_data.pincode is not None:
            address.pincode = address_data.pincode
        if address_data.longitude is not None:
            address.longitude = address_data.longitude
        if address_data.latitude is not None:
            address.latitude = address_data.latitude
        if address_data.map_location_url is not None:
            address.map_location_url = address_data.map_location_url
        if address_data.address_type is not None:
            address.address_type = address_data.address_type
        if address_data.is_default is not None:
            address.is_default = address_data.is_default
        if address_data.is_active is not None:
            address.is_active = address_data.is_active
        
        address.modified_by = modified_by
        address.modified_on = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(address)
        return address

    def delete(self, address_id: int, deleted_by: int):
        """Soft delete a user address."""
        address = self.db.query(LocationUserAddress).filter(
            LocationUserAddress.user_address_id == address_id,
            LocationUserAddress.is_deleted == 'N'
        ).first()
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User address with ID {address_id} not found."
            )
        
        address.is_deleted = 'Y'
        address.deleted_by = deleted_by
        address.deleted_on = datetime.utcnow()
        
        self.db.commit()
        return {"message": f"User address with ID {address_id} has been deleted."}

    def get_active_addresses(self):
        """Fetch all active user addresses."""
        addresses = self.db.query(
            LocationUserAddress,
            User.full_name,
            LocationMaster.location_name,
            LocationActivePincode.pincode.label('pincode_value')
        ).join(
            User, LocationUserAddress.user_id == User.user_id
        ).join(
            LocationMaster, LocationUserAddress.location_id == LocationMaster.location_id
        ).join(
            LocationActivePincode, LocationUserAddress.pincode_id == LocationActivePincode.pincode_id
        ).filter(
            LocationUserAddress.is_active == 'Y',
            LocationUserAddress.is_deleted == 'N'
        ).all()
        
        result = []
        for address, user_name, location_name, pincode_value in addresses:
            address_dict = {
                "user_address_id": address.user_address_id,
                "user_id": address.user_id,
                "location_id": address.location_id,
                "pincode_id": address.pincode_id,
                "address_line1": address.address_line1,
                "address_line2": address.address_line2,
                "city": address.city,
                "pincode": address.pincode,
                "longitude": address.longitude,
                "latitude": address.latitude,
                "map_location_url": address.map_location_url,
                "address_type": address.address_type,
                "is_default": address.is_default,
                "is_active": address.is_active,
                "added_by": address.added_by,
                "added_on": address.added_on,
                "modified_by": address.modified_by,
                "modified_on": address.modified_on,
                "deleted_by": address.deleted_by,
                "deleted_on": address.deleted_on,
                "is_deleted": address.is_deleted,
                "user_name": user_name,
                "location_name": location_name,
                "pincode_value": pincode_value
            }
            result.append(address_dict)
        
        return result

    def get_inactive_addresses(self):
        """Fetch all inactive user addresses."""
        addresses = self.db.query(
            LocationUserAddress,
            User.full_name,
            LocationMaster.location_name,
            LocationActivePincode.pincode.label('pincode_value')
        ).join(
            User, LocationUserAddress.user_id == User.user_id
        ).join(
            LocationMaster, LocationUserAddress.location_id == LocationMaster.location_id
        ).join(
            LocationActivePincode, LocationUserAddress.pincode_id == LocationActivePincode.pincode_id
        ).filter(
            LocationUserAddress.is_active == 'N',
            LocationUserAddress.is_deleted == 'N'
        ).all()
        
        result = []
        for address, user_name, location_name, pincode_value in addresses:
            address_dict = {
                "user_address_id": address.user_address_id,
                "user_id": address.user_id,
                "location_id": address.location_id,
                "pincode_id": address.pincode_id,
                "address_line1": address.address_line1,
                "address_line2": address.address_line2,
                "city": address.city,
                "pincode": address.pincode,
                "longitude": address.longitude,
                "latitude": address.latitude,
                "map_location_url": address.map_location_url,
                "address_type": address.address_type,
                "is_default": address.is_default,
                "is_active": address.is_active,
                "added_by": address.added_by,
                "added_on": address.added_on,
                "modified_by": address.modified_by,
                "modified_on": address.modified_on,
                "deleted_by": address.deleted_by,
                "deleted_on": address.deleted_on,
                "is_deleted": address.is_deleted,
                "user_name": user_name,
                "location_name": location_name,
                "pincode_value": pincode_value
            }
            result.append(address_dict)
        
        return result

    def get_by_user_id(self, user_id: int):
        """Fetch all addresses for a specific user."""
        addresses = self.db.query(
            LocationUserAddress,
            User.full_name,
            LocationMaster.location_name,
            LocationActivePincode.pincode.label('pincode_value')
        ).join(
            User, LocationUserAddress.user_id == User.user_id
        ).join(
            LocationMaster, LocationUserAddress.location_id == LocationMaster.location_id
        ).join(
            LocationActivePincode, LocationUserAddress.pincode_id == LocationActivePincode.pincode_id
        ).filter(
            LocationUserAddress.user_id == user_id,
            LocationUserAddress.is_deleted == 'N'
        ).all()
        
        result = []
        for address, user_name, location_name, pincode_value in addresses:
            address_dict = {
                "user_address_id": address.user_address_id,
                "user_id": address.user_id,
                "location_id": address.location_id,
                "pincode_id": address.pincode_id,
                "address_line1": address.address_line1,
                "address_line2": address.address_line2,
                "city": address.city,
                "pincode": address.pincode,
                "longitude": address.longitude,
                "latitude": address.latitude,
                "map_location_url": address.map_location_url,
                "address_type": address.address_type,
                "is_default": address.is_default,
                "is_active": address.is_active,
                "added_by": address.added_by,
                "added_on": address.added_on,
                "modified_by": address.modified_by,
                "modified_on": address.modified_on,
                "deleted_by": address.deleted_by,
                "deleted_on": address.deleted_on,
                "is_deleted": address.is_deleted,
                "user_name": user_name,
                "location_name": location_name,
                "pincode_value": pincode_value
            }
            result.append(address_dict)
        
        return result

    def toggle_active_status(self, address_id: int, modified_by: int):
        """Toggle the active status of a user address."""
        address = self.db.query(LocationUserAddress).filter(
            LocationUserAddress.user_address_id == address_id,
            LocationUserAddress.is_deleted == 'N'
        ).first()
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User address with ID {address_id} not found."
            )
        
        address.is_active = 'N' if address.is_active == 'Y' else 'Y'
        address.modified_by = modified_by
        address.modified_on = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(address)
        return address

    def toggle_default_status(self, address_id: int, modified_by: int):
        """Toggle the default status of a user address."""
        address = self.db.query(LocationUserAddress).filter(
            LocationUserAddress.user_address_id == address_id,
            LocationUserAddress.is_deleted == 'N'
        ).first()
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User address with ID {address_id} not found."
            )
        
        # If setting as default, unset other addresses for the same user
        if address.is_default == 'N':
            self.db.query(LocationUserAddress).filter(
                LocationUserAddress.user_id == address.user_id,
                LocationUserAddress.is_deleted == 'N'
            ).update({"is_default": "N"})
        
        address.is_default = 'Y' if address.is_default == 'N' else 'N'
        address.modified_by = modified_by
        address.modified_on = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(address)
        return address