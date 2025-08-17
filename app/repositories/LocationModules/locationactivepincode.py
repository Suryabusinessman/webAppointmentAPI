from sqlalchemy.orm import Session
from app.models.LocationModules.locationactivepincode import LocationActivePincode
from app.models.LocationModules.locationmaster import LocationMaster
from app.schemas.LocationModules.locationactivepincode import LocationActivePincodeCreate, LocationActivePincodeUpdate
from fastapi import HTTPException, status
from datetime import datetime

class LocationActivePincodeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        """Fetch all pincodes (both active and inactive) that are not deleted."""
        pincodes = self.db.query(
            LocationActivePincode,
            LocationMaster.location_name
        ).join(
            LocationMaster,
            LocationActivePincode.location_id == LocationMaster.location_id
        ).filter(
            LocationActivePincode.is_deleted == 'N'
        ).all()
        
        if not pincodes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pincodes found in the database."
            )
        
        # Combine pincode data with location name
        result = []
        for pincode, location_name in pincodes:
            pincode_dict = {
                "pincode_id": pincode.pincode_id,
                "pincode": pincode.pincode,
                "location_id": pincode.location_id,
                "location_name": location_name,
                "location_status": pincode.location_status,
                "is_active": pincode.is_active,
                "added_by": pincode.added_by,
                "added_on": pincode.added_on,
                "modified_by": pincode.modified_by,
                "modified_on": pincode.modified_on,
                "deleted_by": pincode.deleted_by,
                "deleted_on": pincode.deleted_on,
                "is_deleted": pincode.is_deleted
            }
            result.append(pincode_dict)
        
        return result

    def get_active_pincodes(self):
        """Fetch all active pincodes."""
        pincodes = self.db.query(
            LocationActivePincode,
            LocationMaster.location_name
        ).join(
            LocationMaster,
            LocationActivePincode.location_id == LocationMaster.location_id
        ).filter(
            LocationActivePincode.is_deleted == 'N',
            LocationActivePincode.is_active == 'Y'
        ).all()
        
        if not pincodes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active pincodes found in the database."
            )
        
        # Combine pincode data with location name
        result = []
        for pincode, location_name in pincodes:
            pincode_dict = {
                "pincode_id": pincode.pincode_id,
                "pincode": pincode.pincode,
                "location_id": pincode.location_id,
                "location_name": location_name,
                "location_status": pincode.location_status,
                "is_active": pincode.is_active,
                "added_by": pincode.added_by,
                "added_on": pincode.added_on,
                "modified_by": pincode.modified_by,
                "modified_on": pincode.modified_on,
                "deleted_by": pincode.deleted_by,
                "deleted_on": pincode.deleted_on,
                "is_deleted": pincode.is_deleted
            }
            result.append(pincode_dict)
        
        return result

    def get_inactive_pincodes(self):
        """Fetch all inactive pincodes."""
        pincodes = self.db.query(
            LocationActivePincode,
            LocationMaster.location_name
        ).join(
            LocationMaster,
            LocationActivePincode.location_id == LocationMaster.location_id
        ).filter(
            LocationActivePincode.is_deleted == 'N',
            LocationActivePincode.is_active == 'N'
        ).all()
        
        if not pincodes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No inactive pincodes found in the database."
            )
        
        # Combine pincode data with location name
        result = []
        for pincode, location_name in pincodes:
            pincode_dict = {
                "pincode_id": pincode.pincode_id,
                "pincode": pincode.pincode,
                "location_id": pincode.location_id,
                "location_name": location_name,
                "location_status": pincode.location_status,
                "is_active": pincode.is_active,
                "added_by": pincode.added_by,
                "added_on": pincode.added_on,
                "modified_by": pincode.modified_by,
                "modified_on": pincode.modified_on,
                "deleted_by": pincode.deleted_by,
                "deleted_on": pincode.deleted_on,
                "is_deleted": pincode.is_deleted
            }
            result.append(pincode_dict)
        
        return result

    def get_by_id(self, pincode_id: int):
        """Fetch a pincode by its ID."""
        result = self.db.query(
            LocationActivePincode,
            LocationMaster.location_name
        ).join(
            LocationMaster,
            LocationActivePincode.location_id == LocationMaster.location_id
        ).filter(
            LocationActivePincode.pincode_id == pincode_id,
            LocationActivePincode.is_deleted == 'N'
        ).first()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pincode with ID {pincode_id} not found."
            )
        
        pincode, location_name = result
        
        # Return pincode object with location_name attribute added
        pincode.location_name = location_name
        return pincode

    def get_by_pincode(self, pincode: str):
        """Fetch a pincode by its value."""
        pincode_obj = self.db.query(LocationActivePincode).filter(
            LocationActivePincode.pincode == pincode,
            LocationActivePincode.is_deleted == 'N'
        ).first()
        return pincode_obj

    def create(self, pincode_data: LocationActivePincodeCreate, added_by: int):
        """Create a new pincode."""
        # Check if a pincode with the same value already exists
        existing_pincode = self.db.query(LocationActivePincode).filter(
            LocationActivePincode.pincode == pincode_data.pincode,
            LocationActivePincode.is_deleted == 'N'
        ).first()

        if existing_pincode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pincode '{pincode_data.pincode}' already exists."
            )

        new_pincode = LocationActivePincode(
            pincode=pincode_data.pincode,
            location_id=pincode_data.location_id,
            location_status=pincode_data.location_status,
            is_active=pincode_data.is_active,
            is_deleted='N',
            added_by=added_by,
            added_on=datetime.utcnow()
        )
        self.db.add(new_pincode)
        self.db.commit()
        self.db.refresh(new_pincode)
        return new_pincode

    def update(self, pincode_id: int, pincode_data: LocationActivePincodeUpdate, modified_by: int):
        """Update an existing pincode."""
        pincode = self.get_by_id(pincode_id)
        
        if pincode_data.pincode:
            existing_pincode = self.get_by_pincode(pincode_data.pincode)
            if existing_pincode and existing_pincode.pincode_id != pincode_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Pincode '{pincode_data.pincode}' already exists."
                )
            pincode.pincode = pincode_data.pincode
        
        if pincode_data.location_id:
            pincode.location_id = pincode_data.location_id
        if pincode_data.location_status:
            pincode.location_status = pincode_data.location_status
        if pincode_data.is_active:
            pincode.is_active = pincode_data.is_active
        
        pincode.modified_by = modified_by
        pincode.modified_on = datetime.utcnow()
        self.db.commit()
        self.db.refresh(pincode)
        return pincode

    def delete(self, pincode_id: int, deleted_by: int):
        """Soft delete a pincode."""
        pincode = self.get_by_id(pincode_id)
        pincode.is_deleted = 'Y'
        pincode.deleted_by = deleted_by
        pincode.deleted_on = datetime.utcnow()
        self.db.commit()
        return {"detail": f"Pincode with ID {pincode_id} has been deleted."}

    def toggle_active_status(self, pincode_id: int, modified_by: int):
        """Toggle the active status of a pincode."""
        pincode = self.get_by_id(pincode_id)
        
        # Toggle the active status
        pincode.is_active = 'N' if pincode.is_active == 'Y' else 'Y'
        pincode.modified_by = modified_by
        pincode.modified_on = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(pincode)
        return pincode