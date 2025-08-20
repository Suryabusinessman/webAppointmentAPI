from fastapi import APIRouter
from app.api.v1.routers import auth, websocket

# Import all routers from different modules
from app.api.v1.routers.UserModules import authrouter, users, usertypes, userpermissions, pages, GoogleSignIn
from app.api.v1.routers.BusinessModules import businessmanuser, businesstype, businesscategories
from app.api.v1.routers.LocationModules import locationmaster, locationactivepincode, locationuseraddress
from app.api.v1.routers.NotificationModules import notification_router
from app.api.v1.routers.NewsModules.newspost import router as newspost_router

# Create the main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])

# User Modules
api_router.include_router(authrouter.router, prefix="/user/auth", tags=["User Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
api_router.include_router(usertypes.router, prefix="/user-types", tags=["User Types"])
api_router.include_router(userpermissions.router, prefix="/user-permissions", tags=["User Permissions"])
api_router.include_router(pages.router, prefix="/pages", tags=["Pages"])
api_router.include_router(GoogleSignIn.router, prefix="/google-auth", tags=["Google Authentication"])

# Business Modules
api_router.include_router(businessmanuser.router, prefix="/business-users", tags=["Business Users"])
api_router.include_router(businesstype.router, prefix="/business-types", tags=["Business Types"])
api_router.include_router(businesscategories.router, prefix="/business-categories", tags=["Business Categories"])

# Location Modules
api_router.include_router(locationmaster.router, prefix="/locations", tags=["Location Management"])
api_router.include_router(locationactivepincode.router, prefix="/location-pincodes", tags=["Location Pincodes"])
api_router.include_router(locationuseraddress.router, prefix="/user-addresses", tags=["User Addresses"])
api_router.include_router(notification_router.router, tags=["Notifications"])

# News Modules
api_router.include_router(newspost_router, prefix="/news", tags=["News Management"])

# Import additional news routers
from app.api.v1.routers.NewsModules.newscomments import router as newscomments_router
from app.api.v1.routers.NewsModules.newslike import router as newslike_router
from app.api.v1.routers.NewsModules.newsshare import router as newsshare_router

# Include additional news routers
api_router.include_router(newscomments_router, prefix="/news", tags=["News Comments"])
api_router.include_router(newslike_router, prefix="/news", tags=["News Likes"])
api_router.include_router(newsshare_router, prefix="/news", tags=["News Shares"])

# Root endpoint
@api_router.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "AppointmentTech API v1",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "auth": "/api/v1/auth",
            "websocket": "/api/v1/ws",
            "user_auth": "/api/v1/user/auth",
            "users": "/api/v1/users",
            "business_users": "/api/v1/business-users",
            "locations": "/api/v1/locations",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# Health check endpoint
@api_router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "message": "AppointmentTech API is running with enhanced security",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0",
        "security_features": [
            "Enhanced JWT tokens",
            "Rate limiting",
            "IP blocking",
            "Device fingerprinting",
            "Security event logging",
            "Suspicious activity detection"
        ]
    } 