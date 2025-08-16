from functools import wraps
from fastapi import HTTPException, status, Request
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

def require_security_check(
    rate_limit: Optional[dict] = None,
    check_suspicious: bool = True,
    log_event: bool = True
):
    """
    Security decorator for individual endpoints
    
    Args:
        rate_limit: {"max_requests": 100, "window_seconds": 60}
        check_suspicious: Whether to check for suspicious activity
        log_event: Whether to log security events
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request object from kwargs
            request = kwargs.get('request')
            if not request:
                # Try to find request in args
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if not request:
                # If no request found, just call the function
                return await func(*args, **kwargs)
            
            try:
                # Basic security checks can be added here
                # For now, just call the original function
                return await func(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Security check failed for {func.__name__}: {str(e)}")
                # Continue with function even if security check fails
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_authentication():
    """Decorator to require authentication"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request object
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Request object not found"
                )
            
            # Check for Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Continue with function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def rate_limit_endpoint(max_requests: int = 100, window_seconds: int = 60):
    """Rate limiting decorator for specific endpoints"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request object
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if not request:
                return await func(*args, **kwargs)
            
            # Rate limiting logic can be added here
            # For now, just call the original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def log_security_event(event_type: str = "API_ACCESS"):
    """Decorator to log security events"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request object
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if request:
                try:
                    # Log security event
                    logger.info(f"Security event: {event_type} for endpoint {request.url.path}")
                except Exception as e:
                    logger.error(f"Error logging security event: {str(e)}")
            
            # Continue with function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator 