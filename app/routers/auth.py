from fastapi import APIRouter, Depends, HTTPException
from app.auth.jwt import create_access_token, verify_token
from app.auth.password import verify_password
from app.models.UserModules.users import User
from app.schemas.UserModules.users import UserLogin, UserResponse
from app.repositories.UserModules.users import UserRepository
from app.core.security import get_current_user

router = APIRouter()

@router.post("/login", response_model=UserResponse)
async def login(user_login: UserLogin):
    user = await UserRepository.get_user_by_email(user_login.email)
    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(sub=user.email)
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user