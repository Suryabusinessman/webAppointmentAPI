from fastapi import APIRouter, Depends, HTTPException
from app.schemas.roles import RoleCreate, RoleUpdate, RoleOut
from app.repositories.roles import RoleRepository
from app.dependencies import get_current_user, get_db
from app.models.roles import Role
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/", response_model=RoleOut)
def create_role(role: RoleCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    return RoleRepository.create_role(db=db, role=role)

@router.get("/{role_id}", response_model=RoleOut)
def read_role(role_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    role = RoleRepository.get_role(db=db, role_id=role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/{role_id}", response_model=RoleOut)
def update_role(role_id: int, role: RoleUpdate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    updated_role = RoleRepository.update_role(db=db, role_id=role_id, role=role)
    if updated_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return updated_role

@router.delete("/{role_id}", response_model=dict)
def delete_role(role_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    success = RoleRepository.delete_role(db=db, role_id=role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"detail": "Role deleted successfully"}