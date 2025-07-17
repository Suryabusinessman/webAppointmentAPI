from fastapi import APIRouter, HTTPException, Depends, status, Header, File, UploadFile, Form, Request
from sqlalchemy.orm import Session
from app.schemas.BusinessModules.businesstype import BusinessTypeCreate, BusinessTypeUpdate, BusinessTypeOut
from app.services.BusinessModules.businesstype import BusinessTypeService
from app.repositories.BusinessModules.businesstype import BusinessTypeRepository
from app.core.database import get_db
from dotenv import load_dotenv
import os
from typing import Optional, List

load_dotenv()
SECURITY_KEY = os.getenv("SECRET_KEY")

router = APIRouter()

UPLOAD_DIRECTORY = "uploads/business_media"

def validate_security_key(provided_key: str):
    """Validate the security key for API access."""
    if provided_key != SECURITY_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid security key."
        )

@router.get("/all-businesstypes", response_model=dict)
def get_all_business_types(
    request: Request,
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
    business_types_data = service.get_all_business_types(security_key)
    
    business_types_out = []
    for bt in business_types_data["data"]:
        bt_out = BusinessTypeOut.from_orm(bt)
        if bt.Business_Media:
            bt_out.Business_Media_URL = f"{request.base_url}{UPLOAD_DIRECTORY}/{bt.Business_Media}"
        business_types_out.append(bt_out)

    return {
        "status": "success",
        "message": "Business types retrieved successfully.",
        "data": business_types_out
    }

@router.get("/businesstypes/{business_type_id}", response_model=dict)
def get_business_type(
    business_type_id: int,
    request: Request,
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
    business_type_data = service.get_business_type_by_id(business_type_id, security_key)
    
    bt = business_type_data["data"]
    bt_out = BusinessTypeOut.from_orm(bt)
    if bt.Business_Media:
        bt_out.Business_Media_URL = f"{request.base_url}{UPLOAD_DIRECTORY}/{bt.Business_Media}"

    return {
        "status": "success",
        "message": "Business type retrieved successfully.",
        "data": bt_out
    }

@router.post("/add-businesstypes", response_model=dict)
def create_business_type(
    request: Request,
    business_type_name: str = Form(...),
    business_type_desc: Optional[str] = Form(None),
    business_code: Optional[str] = Form(None),
    business_status: Optional[str] = Form(None),
    is_active: str = Form('Y'),
    business_media: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    """
    Create a new business type with an optional file upload.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)

    business_type_data = BusinessTypeCreate(
        Business_Type_Name=business_type_name,
        Business_Type_Desc=business_type_desc,
        Business_Code=business_code,
        Business_Status=business_status,
        Is_Active=is_active,
    )

    service = BusinessTypeService(BusinessTypeRepository(db), SECURITY_KEY)
    new_business_type_data = service.create_business_type(business_type_data, business_media, security_key, added_by=1)
    
    bt = new_business_type_data["data"]
    bt_out = BusinessTypeOut.from_orm(bt)
    if bt.Business_Media:
        bt_out.Business_Media_URL = f"{request.base_url}{UPLOAD_DIRECTORY}/{bt.Business_Media}"

    if new_business_type_data["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=new_business_type_data["message"]
        )
    return {
        "status": "success",
        "message": "Business type created successfully.",
        "data": bt_out
    }

@router.put("/update-businesstypes/{business_type_id}", response_model=dict)
def update_business_type(
    business_type_id: int,
    request: Request,
    business_type_name: Optional[str] = Form(None),
    business_type_desc: Optional[str] = Form(None),
    business_code: Optional[str] = Form(None),
    business_status: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
    business_media: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    """
    Update an existing business type with an optional file upload.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)

    business_type_data = BusinessTypeUpdate(
        Business_Type_Name=business_type_name,
        Business_Type_Desc=business_type_desc,
        Business_Code=business_code,
        Business_Status=business_status,
        Is_Active=is_active,
    )

    service = BusinessTypeService(BusinessTypeRepository(db), SECURITY_KEY)
    updated_business_type_data = service.update_business_type(business_type_id, business_type_data, business_media, security_key, modified_by=1)
    
    bt = updated_business_type_data["data"]
    bt_out = BusinessTypeOut.from_orm(bt)
    if bt.Business_Media:
        bt_out.Business_Media_URL = f"{request.base_url}{UPLOAD_DIRECTORY}/{bt.Business_Media}"

    if updated_business_type_data["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=updated_business_type_data["message"]
        )
    return {
        "status": "success",
        "message": "Business type updated successfully.",
        "data": bt_out
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