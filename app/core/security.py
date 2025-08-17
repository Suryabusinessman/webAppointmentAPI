from fastapi import Security, HTTPException, status, Depends, Request
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
import hashlib
import secrets
from app.core.config import config

# Security settings
API_KEY_NAME = "X-API-Key"
API_KEY = config.SECRET_KEY

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES

# Security headers
api_key_header = APIKeyHeader(name=API_KEY_NAME)
http_bearer = HTTPBearer()

# CORS settings
origins = config.CORS_ORIGINS

class SecurityManager:
    """Enhanced centralized security management class"""
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token with enhanced security"""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32),  # JWT ID for token uniqueness
            "type": "access"
        })
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token with enhanced validation"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Additional security checks
            if payload.get("type") != "access":
                return None
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                return None
                
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def get_api_key(api_key: str = Security(api_key_header)) -> str:
        """Validate API key"""
        if api_key != API_KEY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate API key"
            )
        return api_key
    
    @staticmethod
    def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)) -> Dict[str, Any]:
        """Get current user from JWT token with enhanced validation"""
        token = credentials.credentials
        payload = SecurityManager.verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_csrf_token(token: str, stored_token: str) -> bool:
        """Validate CSRF token"""
        return secrets.compare_digest(token, stored_token)
    
    @staticmethod
    def hash_device_fingerprint(device_info: str, ip_address: str) -> str:
        """Create a hash of device fingerprint for session tracking"""
        fingerprint = f"{device_info}:{ip_address}"
        return hashlib.sha256(fingerprint.encode()).hexdigest()

def validate_security_key(provided_key: str, expected_key: str = API_KEY):
    """Validate security key for API access - Enhanced version"""
    if not provided_key or provided_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid security key"
        )

def require_permissions(required_permissions: list):
    """Decorator to require specific permissions"""
    def dependency(current_user: Dict[str, Any] = Depends(SecurityManager.get_current_user)):
        user_permissions = current_user.get("permissions", [])
        if not all(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return dependency

def require_role(required_role_id: int):
    """Decorator to require specific user role"""
    def dependency(current_user: Dict[str, Any] = Depends(SecurityManager.get_current_user)):
        user_role_id = current_user.get("user_type_id")
        if user_role_id != required_role_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions"
            )
        return current_user
    return dependency

def validate_request_origin(request: Request):
    """Validate request origin for additional security"""
    origin = request.headers.get("origin")
    if origin and origin not in origins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid request origin"
        )

# Enhanced rate limiting with IP-based tracking
class EnhancedRateLimiter:
    """Enhanced rate limiting implementation with IP tracking"""
    
    def __init__(self):
        self.requests = {}
        self.blocked_ips = {}
    
    def is_allowed(self, client_id: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """Check if request is allowed based on rate limiting with IP blocking"""
        now = datetime.utcnow()
        
        # Check if IP is blocked
        if client_id in self.blocked_ips:
            if (now - self.blocked_ips[client_id]).seconds < 3600:  # 1 hour block
                return False
            else:
                del self.blocked_ips[client_id]
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if (now - req_time).seconds < window_seconds
        ]
        
        if len(self.requests[client_id]) >= max_requests:
            # Block IP for 1 hour if rate limit exceeded
            self.blocked_ips[client_id] = now
            return False
        
        self.requests[client_id].append(now)
        return True

# Global enhanced rate limiter instance
enhanced_rate_limiter = EnhancedRateLimiter()

def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """Enhanced decorator for rate limiting"""
    def dependency(request: Request):
        client_id = request.client.host
        if not enhanced_rate_limiter.is_allowed(client_id, max_requests, window_seconds):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        return client_id
    return dependency

# Middleware configuration
def add_cors_middleware(app):
    """Add CORS middleware to FastAPI app with enhanced security"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS","PATCH"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time", "X-Request-ID"],
    )

# Security headers middleware
def add_security_headers_middleware(app):
    """Add security headers middleware"""
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        
        # SECURITY: Enhanced security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # SECURITY: HTTPS enforcement
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # SECURITY: Content Security Policy
        # response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        # SECURITY: Content Security Policy - Allow Swagger UI resources
        # response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' https://fastapi.tiangolo.com; font-src 'self' https://cdn.jsdelivr.net;"
        
        return response

# Request validation middleware
def add_request_validation_middleware(app):
    """Add request validation middleware"""
    @app.middleware("http")
    async def request_validation_middleware(request: Request, call_next):
        # Validate request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request too large"
            )
        
        # Add request ID for tracking
        request_id = secrets.token_urlsafe(16)
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response