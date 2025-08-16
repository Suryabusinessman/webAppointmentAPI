from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.jwt import get_current_user
from app.models.UserModules.users import User

# Dependency to get the current user
def get_current_active_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return current_user

# Dependency to get the database session
def get_db_session():
    db = get_db()
    try:
        yield db
    finally:
        db.close()