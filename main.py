# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# # from app.core.security import add_cors_middleware
# from app.core.middleware import add_middleware
# from app.api.v1.routers import user, auth, pages, roles
# from app.core.config import config

# app = FastAPI()
# # add_cors_middleware(app)
# add_middleware(app)
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=config.ALLOW_ORIGINS,
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# app.include_router(user.router, prefix="/api/v1/users", tags=["users"])
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(pages.router, prefix="/api/v1/pages", tags=["pages"])
# app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the FastAPI application!"}


import os
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

from app.core.middleware import add_middleware
from app.api.v1.routers import auth
from app.api.v1.routers.UserModules import usertypes, users,authrouter,pages,userpermissions,GoogleSignIn  # Import the usertypes router
from app.api.v1.routers.BusinessModules import businesstype, businessmanuser, businesscategories
from app.api.v1.routers.LocationModules import locationmaster, locationactivepincode, locationuseraddress
from app.core.config import config

# Load environment variables from .env
load_dotenv()

# Define the API key header
API_KEY_NAME = "EAE2F9F6896FF6FC7B54446BA6D5B"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Dependency to validate the API key
def validate_api_key(api_key: str = Security(api_key_header)):
    expected_api_key = os.getenv("EAE2F9F6896FF6FC7B54446BA6D5B")  # Read from .env
    if api_key != expected_api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Invalid API key"
        )
    return api_key

# Initialize FastAPI app
app = FastAPI(
    title="Appointment",  # Change the title here
    description="This is a custom FastAPI project with role-based access control.",
    version="1.0.0"
)

# Add middleware
add_middleware(app)

# Mount the static files directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers with API key validation
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"], dependencies=[Depends(validate_api_key)])
# app.include_router(pages.router, prefix="/api/v1/pages", tags=["pages"], dependencies=[Depends(validate_api_key)])
# app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"], dependencies=[Depends(validate_api_key)])
# Include the usertypes router with API key validation
app.include_router(
    usertypes.router, 
    prefix="/api/v1/usertypes", 
    tags=["usertypes"], 
    dependencies=[Depends(validate_api_key)]
)
app.include_router(
    users.router, 
    prefix="/api/v1/users", 
    tags=["users"], 
    dependencies=[Depends(validate_api_key)]
)
app.include_router(
    authrouter.router, 
    prefix="/api/v1/authrouter", 
    tags=["authrouter"], 
    dependencies=[Depends(validate_api_key)]
)
app.include_router(
    pages.router, 
    prefix="/api/v1/pages", 
    tags=["pages"], 
    dependencies=[Depends(validate_api_key)]
)
app.include_router(
    userpermissions.router, 
    prefix="/api/v1/userpermissions", 
    tags=["userpermissions"], 
    dependencies=[Depends(validate_api_key)]
)
app.include_router(
    businesstype.router, 
    prefix="/api/v1/businesstype", 
    tags=["businesstype"], 
    dependencies=[Depends(validate_api_key)]
)
app.include_router(
    businessmanuser.router, 
    prefix="/api/v1/businessmanuser", 
    tags=["businessmanuser"], 
    dependencies=[Depends(validate_api_key)]
)
app.include_router(
    businesscategories.router, 
    prefix="/api/v1/businesscategories", 
    tags=["businesscategories"], 
    dependencies=[Depends(validate_api_key)]
)
app.include_router(
    locationmaster.router, 
    prefix="/api/v1/locationmaster", 
    tags=["locationmaster"], 
    dependencies=[Depends(validate_api_key)]
)
app.include_router(
    locationactivepincode.router, 
    prefix="/api/v1/locationactivepincode", 
    tags=["locationactivepincode"], 
    dependencies=[Depends(validate_api_key)]
)
app.include_router(
    locationuseraddress.router, 
    prefix="/api/v1/locationuseraddress", 
    tags=["locationuseraddress"], 
    dependencies=[Depends(validate_api_key)]
)
app.include_router(
    GoogleSignIn.router,
    prefix="/api/v1/GoogleSignIn", 
    tags=["GoogleSignIn"], 
    dependencies=[Depends(validate_api_key)]
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}