from fastapi import APIRouter, Depends, HTTPException
from app.auth.jwt import create_access_token, verify_token,get_current_user
from app.schemas.UserModules.users import UserLogin, UserResponse
from app.repositories.UserModules.users import UserRepository
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.v1.dependencies import get_db_session
# from app.core.security import get_current_user

router = APIRouter()

@router.post("/login", response_model=UserResponse)
async def login(user_login: UserLogin):
    user = await UserRepository.get_user_by_email(user_login.email)
    if not user or not verify_token(user_login.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(sub=user.email)
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session),
):
    # Validate user credentials
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(form_data.username)
    if not user or not user_repo.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}