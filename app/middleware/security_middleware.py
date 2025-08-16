from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import hashlib
import json
import logging
from typing import Dict, Any, Optional
import re

from app.services.SecurityModules.security_service import SecurityService
from app.models.SecurityModules.security_events import SecurityEventType, SecurityEventSeverity
from app.core.database import get_db

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Optimized security middleware for all APIs - No IP blocking"""
    
    def __init__(self):
        self.rate_limit_cache = {}
        self.suspicious_ips = {}
        self.security_service = None
    
    def get_security_service(self, db: Session) -> SecurityService:
        """Get security service instance"""
        if not self.security_service:
            self.security_service = SecurityService(db)
        return self.security_service
    
    def extract_device_info(self, request: Request) -> tuple[str, str]:
        """Extract device information and IP address"""
        device_info = request.headers.get("User-Agent", "Unknown Device")
        
        # Get IP address
        ip_address = request.headers.get("X-Forwarded-For")
        if ip_address:
            ip_address = ip_address.split(",")[0].strip()
        else:
            ip_address = request.client.host
        
        return device_info, ip_address
    
    def generate_device_fingerprint(self, user_agent: str, ip_address: str, headers: Dict[str, str]) -> str:
        """Generate device fingerprint"""
        try:
            device_info = {
                'user_agent': user_agent,
                'ip_address': ip_address,
                'accept_language': headers.get('accept-language', ''),
                'accept_encoding': headers.get('accept-encoding', ''),
                'sec_ch_ua': headers.get('sec-ch-ua', ''),
                'sec_ch_ua_platform': headers.get('sec-ch-ua-platform', ''),
            }
            
            fingerprint_data = json.dumps(device_info, sort_keys=True)
            return hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error generating device fingerprint: {str(e)}")
            return hashlib.sha256(f"{user_agent}:{ip_address}".encode()).hexdigest()
    
    def check_rate_limit(self, ip_address: str, endpoint: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """Check rate limiting with optimized caching"""
        try:
            now = datetime.utcnow()
            key = f"{ip_address}:{endpoint}"
            
            # Clean old entries
            if key in self.rate_limit_cache:
                self.rate_limit_cache[key] = [
                    timestamp for timestamp in self.rate_limit_cache[key]
                    if (now - timestamp).seconds < window_seconds
                ]
            else:
                self.rate_limit_cache[key] = []
            
            # Check if limit exceeded
            if len(self.rate_limit_cache[key]) >= max_requests:
                return False
            
            # Add current request
            self.rate_limit_cache[key].append(now)
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            return True
    
    def check_malicious_patterns(self, request_data: Dict[str, Any]) -> bool:
        """Check for malicious patterns"""
        try:
            # SQL injection patterns
            sql_patterns = [
                r"(\b(union|select|insert|update|delete|drop|create|alter)\b)",
                r"(--|\b(and|or)\b\s+\d+\s*=\s*\d+)",
                r"(\b(script|javascript|vbscript|onload|onerror)\b)",
            ]
            
            request_str = json.dumps(request_data).lower()
            for pattern in sql_patterns:
                if re.search(pattern, request_str, re.IGNORECASE):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking malicious patterns: {str(e)}")
            return False
    
    def calculate_suspicious_score(self, user_id: Optional[int], ip_address: str, device_fingerprint: str, 
                                 request_data: Dict[str, Any], db: Session) -> int:
        """Calculate suspicious activity score (optimized)"""
        try:
            score = 0
            security_service = self.get_security_service(db)
            
            # Check for rapid requests (cached check)
            recent_requests = len([t for t in self.rate_limit_cache.get(f"{ip_address}:all", [])
                                 if (datetime.utcnow() - t).seconds < 300])
            
            if recent_requests > 20:
                score += 25
            elif recent_requests > 10:
                score += 10
            
            # Check for malicious patterns
            if self.check_malicious_patterns(request_data):
                score += 40
            
            # Check for multiple users from same IP (if user_id provided)
            if user_id:
                # Use cached security service for user-specific checks
                # Simplified query to avoid syntax errors
                try:
                    from app.models.SecurityModules.security_events import SecurityEvent
                    failed_attempts = db.query(SecurityEvent).filter(
                        SecurityEvent.user_id == user_id,
                        SecurityEvent.event_type == SecurityEventType.LOGIN_FAILED,
                        SecurityEvent.created_at >= datetime.utcnow() - timedelta(hours=1)
                    ).count()
                    
                    if failed_attempts > 5:
                        score += 30
                    elif failed_attempts > 3:
                        score += 15
                except Exception as e:
                    logger.error(f"Error checking failed attempts: {str(e)}")
            
            return min(score, 100)
            
        except Exception as e:
            logger.error(f"Error calculating suspicious score: {str(e)}")
            return 0
    
    async def process_request(self, request: Request, call_next) -> JSONResponse:
        """Process request with security checks - No IP blocking"""
        try:
            # Get database session
            db = next(get_db())
            
            # Extract device info
            device_info, ip_address = self.extract_device_info(request)
            
            # Get endpoint for rate limiting
            endpoint = request.url.path
            method = request.method
            
            # Skip security checks for health and static endpoints
            if endpoint in ['/health', '/docs', '/redoc', '/openapi.json']:
                return await call_next(request)
            
            # Security checks
            security_service = self.get_security_service(db)
            
            # Rate limiting (different limits for different endpoints)
            rate_limits = {
                "login": {"max_requests": 5, "window_seconds": 300},
                "register": {"max_requests": 3, "window_seconds": 3600},
                "forgot_password": {"max_requests": 3, "window_seconds": 3600},
                "default": {"max_requests": 100, "window_seconds": 60}
            }
            
            # Determine rate limit based on endpoint
            endpoint_key = "default"
            for key in rate_limits:
                if key in endpoint.lower():
                    endpoint_key = key
                    break
            
            limit_config = rate_limits[endpoint_key]
            
            # Check rate limit but don't block - just log
            rate_limit_exceeded = not self.check_rate_limit(ip_address, endpoint, **limit_config)
            if rate_limit_exceeded:
                logger.warning(f"Rate limit exceeded for IP {ip_address} on endpoint {endpoint} - Allowing request")
            
            # Generate device fingerprint
            device_fingerprint = self.generate_device_fingerprint(
                device_info, ip_address, dict(request.headers)
            )
            
            # Calculate suspicious score
            request_data = {
                "path": endpoint,
                "method": method,
                "headers": dict(request.headers),
                "query_params": dict(request.query_params)
            }
            
            # Try to get user_id from token if available
            user_id = None
            try:
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
                    # Decode token to get user_id (simplified)
                    # In production, use proper JWT decoding
                    user_id = None  # Extract from token if needed
            except:
                pass
            
            suspicious_score = self.calculate_suspicious_score(
                user_id, ip_address, device_fingerprint, request_data, db
            )
            
            # Log security event (always log, but don't block)
            try:
                security_service.log_security_event(
                    event_type=SecurityEventType.LOGIN_ATTEMPT if "login" in endpoint else SecurityEventType.API_ACCESS,
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=device_info,
                    device_fingerprint=device_fingerprint,
                    suspicious_score=suspicious_score,
                    severity=SecurityEventSeverity.HIGH if suspicious_score > 70 else SecurityEventSeverity.MEDIUM,
                    event_metadata={
                        "endpoint": endpoint,
                        "method": method,
                        "suspicious_score": suspicious_score,
                        "rate_limit_exceeded": rate_limit_exceeded,
                        "ip_blocking_disabled": True  # Indicate that IP blocking is disabled
                    }
                )
            except Exception as e:
                logger.error(f"Error logging security event: {str(e)}")
            
            # Handle suspicious activity (log only, no blocking)
            if suspicious_score > 90:
                logger.warning(f"High suspicious activity detected for IP {ip_address} (score: {suspicious_score}) - Monitoring only, allowing request")
                # Don't create any blocks - just log for monitoring
            
            # Always allow the request to proceed
            response = await call_next(request)
            
            # Add security info to response headers
            response.headers["X-Security-Score"] = str(suspicious_score)
            response.headers["X-Device-Fingerprint"] = device_fingerprint
            response.headers["X-Rate-Limit-Remaining"] = str(limit_config["max_requests"] - len(self.rate_limit_cache.get(f"{ip_address}:{endpoint}", [])))
            response.headers["X-IP-Blocking-Disabled"] = "true"
            
            return response
            
        except Exception as e:
            logger.error(f"Error in security middleware: {str(e)}")
            # Continue with request even if security check fails
            return await call_next(request)

# Global security middleware instance
security_middleware = SecurityMiddleware()

async def security_middleware_function(request: Request, call_next):
    """FastAPI middleware function"""
    return await security_middleware.process_request(request, call_next) 