from sqlalchemy.orm import Session
from app.models.LocationModules.locationuseraddress import LocationUserAddress
from app.schemas.LocationModules.locationuseraddress import LocationUserAddressCreate, LocationUserAddressUpdate
from fastapi import HTTPException, status
from datetime import datetime


class LocationUserAddressRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        """Fetch all active user addresses."""
        addresses = self.db.query(LocationUserAddress).filter(LocationUserAddress.Is_Deleted == 'N').all()
        if not addresses:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user addresses found in the database."
            )
        return addresses

    def get_by_id(self, address_id: int):
        """Fetch a user address by its ID."""
        address = self.db.query(LocationUserAddress).filter(
            LocationUserAddress.User_Address_Id == address_id,
            LocationUserAddress.Is_Deleted == 'N'
        ).first()
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User address with ID {address_id} not found."
            )
        return address
    def get_by_address(self, address: str):
        """Fetch a user address by its address line."""
        address = self.db.query(LocationUserAddress).filter(
            LocationUserAddress.Address_Line1 == address,
            LocationUserAddress.Is_Deleted == 'N'
        ).first()
        # if not address:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"User address with name {address} not found."
        #     )
        return address
    def create(self, address_data: LocationUserAddressCreate, added_by: int):
        """Create a new user address."""
        # Check if a user address with the same address line already exists
        existing_address = self.db.query(LocationUserAddress).filter(
            LocationUserAddress.Address_Line1 == address_data.Address_Line1,
            LocationUserAddress.Is_Deleted == 'N'
        ).first()

        # Log a message if the user address already exists
        if existing_address:
            print(f"User address with address line '{address_data.Address_Line1}' already exists. Creating a new user address.")
        if existing_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User address with address line '{address_data.Address_Line1}' already exists."
            )
        new_address = LocationUserAddress(
            User_Id=address_data.User_Id,
            Location_Id=address_data.Location_Id,
            Pincode_Id=address_data.Pincode_Id,
            Address_Line1=address_data.Address_Line1,
            Address_Line2=address_data.Address_Line2,
            City=address_data.City,
            Pincode=address_data.Pincode,
            Longitude=address_data.Longitude,
            Latitude=address_data.Latitude,
            Map_Location_Url=address_data.Map_Location_Url,
            Address_Type=address_data.Address_Type,
            Is_Default=address_data.Is_Default,
            Is_Active=address_data.Is_Active,
            Added_By=added_by,
            Added_On=datetime.utcnow()
        )
        self.db.add(new_address)
        self.db.commit()
        self.db.refresh(new_address)
        return new_address
    def update(self, address_id: int, address_data: LocationUserAddressUpdate, modified_by: int):
        """Update an existing user address."""
        address = self.db.query(LocationUserAddress).filter(
            LocationUserAddress.User_Address_Id == address_id,
            LocationUserAddress.Is_Deleted == 'N'
        ).first()
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User address with ID {address_id} not found."
            )
        # for key, value in address_data.dict(exclude_unset=True).items():
        #     setattr(address, key, value)
        if address_data.Address_Line1:
            existing_address = self.get_by_address(address_data.Address_Line1)
            if existing_address and existing_address.User_Address_Id != address_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User address with address line '{address_data.Address_Line1}' already exists."
                )
            address.Address_Line1 = address_data.Address_Line1
        if address_data.Address_Line2:
            address.Address_Line2 = address_data.Address_Line2
        if address_data.City:
            address.City = address_data.City
        if address_data.Pincode:
            address.Pincode = address_data.Pincode
        if address_data.Longitude:
            address.Longitude = address_data.Longitude
        if address_data.Latitude:
            address.Latitude = address_data.Latitude
        if address_data.Map_Location_Url:
            address.Map_Location_Url = address_data.Map_Location_Url
        if address_data.Address_Type:
            address.Address_Type = address_data.Address_Type
        if address_data.Is_Default:
            address.Is_Default = address_data.Is_Default
        if address_data.Is_Active:
            address.Is_Active = address_data.Is_Active
        address.Modified_By = modified_by
        address.Modified_On = datetime.utcnow()
        self.db.commit()
        self.db.refresh(address)
        return address
    def delete(self, address_id: int, deleted_by: int):
        """Soft delete a user address."""
        address = self.db.query(LocationUserAddress).filter(
            LocationUserAddress.User_Address_Id == address_id,
            LocationUserAddress.Is_Deleted == 'N'
        ).first()
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User address with ID {address_id} not found."
            )
        address.Is_Deleted = 'Y'
        address.Deleted_By = deleted_by
        address.Deleted_On = datetime.utcnow()
        self.db.commit()
        return {"message": f"User address with ID {address_id} has been deleted."}