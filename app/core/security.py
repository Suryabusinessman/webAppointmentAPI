from fastapi import Security
from fastapi.security import APIKeyHeader
from starlette.middleware.cors import CORSMiddleware

# Security settings
API_KEY_NAME = "X-API-Key"
API_KEY = "88AC1A95756D9259823CCA6E17145"  # Replace with your actual API key

api_key_header = APIKeyHeader(name=API_KEY_NAME)

# CORS settings
origins = [
    "http://localhost:3000",  # Frontend URL
    "https://yourdomain.com",  # Your production domain
]

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

# Middleware configuration
def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )