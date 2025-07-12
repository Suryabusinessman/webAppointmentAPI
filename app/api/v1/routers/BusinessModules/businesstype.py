from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from app.schemas.BusinessModules.businesstype import BusinessTypeCreate, BusinessTypeUpdate
from app.services.BusinessModules.businesstype import BusinessTypeService
from app.repositories.BusinessModules.businesstype import BusinessTypeRepository
from app.core.database import get_db
from dotenv import load_dotenv
import os

load_dotenv()
SECURITY_KEY = os.getenv("SECRET_KEY")

router = APIRouter()

def validate_security_key(provided_key: str):
    """Validate the security key for API access."""
    if provided_key != SECURITY_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid security key."
        )
    
@router.get("/all-businesstypes", response_model=dict)
def get_all_business_types(
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch all business types.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessTypeService(BusinessTypeRepository(db), SECURITY_KEY)
    business_types = service.get_all_business_types(security_key)
    return {
        "status": "success",
        "message": "Business types retrieved successfully.",
        "data": business_types["data"]
    }

@router.get("/businesstypes/{business_type_id}", response_model=dict)
def get_business_type(
    business_type_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch a business type by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessTypeService(BusinessTypeRepository(db), SECURITY_KEY)
    business_type = service.get_business_type_by_id(business_type_id, security_key)
    return {
        "status": "success",
        "message": "Business type retrieved successfully.",
        "data": business_type["data"]
    }

@router.post("/add-businesstypes", response_model=dict)
def create_business_type(
    business_type: BusinessTypeCreate,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Create a new business type.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessTypeService(BusinessTypeRepository(db), SECURITY_KEY)
    new_business_type = service.create_business_type(business_type, security_key, added_by=1)  # Assuming added_by is 1 for this example
    if new_business_type["status"] == "error":  # Handle error case
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=new_business_type["message"]
        )
    return {
        "status": "success",
        "message": "Business type created successfully.",
        "data": new_business_type["data"]
    }

@router.put("/update-businesstypes/{business_type_id}", response_model=dict)
def update_business_type(
    business_type_id: int,
    business_type: BusinessTypeUpdate,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Update an existing business type.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessTypeService(BusinessTypeRepository(db), SECURITY_KEY)
    updated_business_type = service.update_business_type(business_type_id, business_type, security_key, modified_by=1)  # Assuming modified_by is 1 for this example
    if updated_business_type["status"] == "error":  # Handle error case
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=updated_business_type["message"]
        )
    return {
        "status": "success",
        "message": "Business type updated successfully.",
        "data": updated_business_type["data"]
    }

@router.delete("/delete-businesstypes/{business_type_id}", response_model=dict)
def delete_business_type(
    business_type_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Delete a business type by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessTypeService(BusinessTypeRepository(db), SECURITY_KEY)
    service.delete_business_type(business_type_id, security_key, deleted_by=1)  # Assuming modified_by is 1 for this example
    
    # if service["status"] == "error":
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=service["message"]
    #     )
    return {
        "status": "success",
        "color":"success",
        "message": "Business type deleted successfully."
    }