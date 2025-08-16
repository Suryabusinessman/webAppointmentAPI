from fastapi import Request, HTTPException, status
from typing import Optional, Dict, Any
import hashlib
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SecurityUtils:
    """Utility class for security operations"""
    
    @staticmethod
    def get_client_info(request: Request) -> Dict[str, Any]:
        """Extract client information from request"""
        try:
            # Get IP address
            ip_address = request.headers.get("X-Forwarded-For")
            if ip_address:
                ip_address = ip_address.split(",")[0].strip()
            else:
                ip_address = request.client.host
            
            # Get device info
            user_agent = request.headers.get("User-Agent", "Unknown Device")
            
            # Get additional headers
            headers = {
                'accept-language': request.headers.get('accept-language', ''),
                'accept-encoding': request.headers.get('accept-encoding', ''),
                'sec-ch-ua': request.headers.get('sec-ch-ua', ''),
                'sec-ch-ua-platform': request.headers.get('sec-ch-ua-platform', ''),
            }
            
            return {
                "ip_address": ip_address,
                "user_agent": user_agent,
                "headers": headers,
                "endpoint": request.url.path,
                "method": request.method,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error extracting client info: {str(e)}")
            return {}
    
    @staticmethod
    def generate_device_fingerprint(client_info: Dict[str, Any]) -> str:
        """Generate device fingerprint from client info"""
        try:
            device_data = {
                'user_agent': client_info.get('user_agent', ''),
                'ip_address': client_info.get('ip_address', ''),
                'accept_language': client_info.get('headers', {}).get('accept-language', ''),
                'accept_encoding': client_info.get('headers', {}).get('accept-encoding', ''),
                'sec_ch_ua': client_info.get('headers', {}).get('sec-ch-ua', ''),
                'sec_ch_ua_platform': client_info.get('headers', {}).get('sec-ch-ua-platform', ''),
            }
            
            fingerprint_data = json.dumps(device_data, sort_keys=True)
            return hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error generating device fingerprint: {str(e)}")
            return hashlib.sha256(f"{client_info.get('user_agent', '')}:{client_info.get('ip_address', '')}".encode()).hexdigest()
    
    @staticmethod
    def check_rate_limit_simple(ip_address: str, endpoint: str, cache: Dict[str, list], 
                               max_requests: int = 100, window_seconds: int = 60) -> bool:
        """Simple rate limiting check"""
        try:
            now = datetime.utcnow()
            key = f"{ip_address}:{endpoint}"
            
            # Clean old entries
            if key in cache:
                cache[key] = [
                    timestamp for timestamp in cache[key]
                    if (now - timestamp).seconds < window_seconds
                ]
            else:
                cache[key] = []
            
            # Check if limit exceeded
            if len(cache[key]) >= max_requests:
                return False
            
            # Add current request
            cache[key].append(now)
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            return True
    
    @staticmethod
    def validate_request_simple(request: Request) -> Dict[str, Any]:
        """Simple request validation"""
        try:
            client_info = SecurityUtils.get_client_info(request)
            device_fingerprint = SecurityUtils.generate_device_fingerprint(client_info)
            
            return {
                "valid": True,
                "client_info": client_info,
                "device_fingerprint": device_fingerprint,
                "suspicious_score": 0  # Can be enhanced later
            }
        except Exception as e:
            logger.error(f"Error validating request: {str(e)}")
            return {"valid": False, "error": str(e)}
    
    @staticmethod
    def log_security_event_simple(event_type: str, client_info: Dict[str, Any], 
                                 user_id: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None):
        """Simple security event logging"""
        try:
            event_data = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "client_info": client_info,
                "user_id": user_id,
                "metadata": metadata or {}
            }
            
            logger.info(f"Security Event: {json.dumps(event_data, indent=2)}")
            
        except Exception as e:
            logger.error(f"Error logging security event: {str(e)}")

# Global security utilities instance
security_utils = SecurityUtils()

def quick_security_check(request: Request) -> Dict[str, Any]:
    """Quick security check for any endpoint"""
    return security_utils.validate_request_simple(request)

def log_api_access(request: Request, user_id: Optional[int] = None):
    """Log API access for security monitoring"""
    client_info = security_utils.get_client_info(request)
    security_utils.log_security_event_simple("API_ACCESS", client_info, user_id) 