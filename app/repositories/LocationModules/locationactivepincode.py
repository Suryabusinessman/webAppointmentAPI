from sqlalchemy.orm import Session
from app.models.LocationModules.locationactivepincode import LocationActivePincode
from app.schemas.LocationModules.locationactivepincode import LocationActivePincodeCreate, LocationActivePincodeUpdate
from fastapi import HTTPException, status
from datetime import datetime

class LocationActivePincodeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        """Fetch all active pincodes."""
        pincodes = self.db.query(LocationActivePincode).filter(LocationActivePincode.Is_Deleted == 'N').all()
        if not pincodes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pincodes found in the database."
            )
        return pincodes

    def get_by_id(self, pincode_id: int):
        """Fetch a pincode by its ID."""
        pincode = self.db.query(LocationActivePincode).filter(
            LocationActivePincode.Pincode_Id == pincode_id,
            LocationActivePincode.Is_Deleted == 'N'
        ).first()
        if not pincode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pincode with ID {pincode_id} not found."
            )
        return pincode
    def get_by_pincode(self, pincode: str):
        """Fetch a pincode by its value."""
        pincode = self.db.query(LocationActivePincode).filter(
            LocationActivePincode.Pincode == pincode,
            LocationActivePincode.Is_Deleted == 'N'
        ).first()
        # if not pincode:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Pincode {pincode} not found."
        #     )
        return pincode
    def create(self, pincode_data: LocationActivePincodeCreate, added_by: int):
        """Create a new pincode."""
        # Check if a pincode with the same value already exists
        existing_pincode = self.db.query(LocationActivePincode).filter(
            LocationActivePincode.Pincode == pincode_data.Pincode,
            LocationActivePincode.Is_Deleted == 'N'
        ).first()

        # Log a message if the pincode already exists
        if existing_pincode:
            print(f"Pincode '{pincode_data.Pincode}' already exists. Creating a new pincode.")
        if existing_pincode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pincode '{pincode_data.Pincode}' already exists."
            )
        new_pincode = LocationActivePincode(
            Pincode=pincode_data.Pincode,
            Location_Id=pincode_data.Location_Id,
            Location_Status=pincode_data.Location_Status,
            Is_Active=pincode_data.Is_Active,
            Is_Deleted=pincode_data.Is_Deleted,
            Added_By=added_by,
            Added_On=datetime.utcnow()
        )
        self.db.add(new_pincode)
        self.db.commit()
        self.db.refresh(new_pincode)
        return 
    def update(self, pincode_id: int, pincode_data: LocationActivePincodeUpdate, modified_by: int):
        """Update an existing pincode."""
        pincode = self.db.query(LocationActivePincode).filter(
            LocationActivePincode.Pincode_Id == pincode_id,
            LocationActivePincode.Is_Deleted == 'N'
        ).first()
        if not pincode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pincode with ID {pincode_id} not found."
            )
        if pincode_data.Pincode:
            existing_pincode = self.db.query(LocationActivePincode).filter(
                LocationActivePincode.Pincode == pincode_data.Pincode,
                LocationActivePincode.Is_Deleted == 'N'
            ).first()
            if existing_pincode and existing_pincode.Pincode_Id != pincode_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Pincode '{pincode_data.Pincode}' already exists."
                )
        # Update the pincode attributes
        pincode.Pincode = pincode_data.Pincode
        if pincode_data.Location_Id:
            pincode.Location_Id = pincode_data.Location_Id
        if pincode_data.Location_Status:
            pincode.Location_Status = pincode_data.Location_Status
        if pincode_data.Is_Active:
            pincode.Is_Active = pincode_data.Is_Active
        # for key, value in pincode_data.dict(exclude_unset=True).items():
        #     setattr(pincode, key, value)
        pincode.Modified_By = modified_by
        pincode.Modified_On = datetime.utcnow()
        self.db.commit()
        self.db.refresh(pincode)
        return pincode
    def delete(self, pincode_id: int, deleted_by: int):
        """Soft delete a pincode."""
        pincode = self.db.query(LocationActivePincode).filter(
            LocationActivePincode.Pincode_Id == pincode_id,
            LocationActivePincode.Is_Deleted == 'N'
        ).first()
        if not pincode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pincode with ID {pincode_id} not found."
            )
        pincode.Is_Deleted = 'Y'
        pincode.Deleted_By = deleted_by
        pincode.Deleted_On = datetime.utcnow()
        self.db.commit()
        return {"detail": "Pincode deleted successfully."}