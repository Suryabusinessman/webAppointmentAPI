from fastapi import APIRouter

router = APIRouter()

# Include your API routes here
from .v1.routers import  auth, websocket

# router.include_router(user.router, prefix="/users", tags=["users"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
# router.include_router(pages.router, prefix="/pages", tags=["pages"])
# router.include_router(roles.router, prefix="/roles", tags=["roles"])
router.include_router(websocket.router, prefix="/ws", tags=["websocket"])