from fastapi import FastAPI

app = FastAPI()

# Import routers
from .api.v1.routers import  auth, websocket

# Include routers
# app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(pages.router, prefix="/pages", tags=["pages"])
# app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])