from fastapi import APIRouter

# Create the main router for the v1 API
router = APIRouter()

# Import routers for different features
from .routers import auth, websocket
# from app.api.v1.routers.UserModules import users, usertypes

# Include routers for different modules
# router.include_router(users.router, prefix="/users", tags=["users"])
# router.include_router(usertypes.router, prefix="/usertypes", tags=["usertypes"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
# router.include_router(pages.router, prefix="/pages", tags=["pages"])
# router.include_router(roles.router, prefix="/roles", tags=["roles"])
router.include_router(websocket.router, prefix="/ws", tags=["websocket"])