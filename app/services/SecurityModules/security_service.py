from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import hashlib
import secrets
import json
import logging
import re
from ipaddress import ip_address, IPv4Address, IPv6Address

from app.models.SecurityModules.security_events import SecurityEvent, SecurityEventType, SecurityEventSeverity
from app.models.SecurityModules.security_sessions import SecuritySession, SessionStatus
from app.models.UserModules.users import User
from app.core.security import SecurityManager

logger = logging.getLogger(__name__)

class SecurityService:
    """Comprehensive security service for authentication and threat detection - No IP blocking"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rate_limit_cache = {}
        self.suspicious_ips = {}
    
    # ==================== DEVICE FINGERPRINTING ====================
    
    def generate_device_fingerprint(self, user_agent: str, ip_address: str, headers: Dict[str, str]) -> str:
        """Generate a unique device fingerprint"""
        try:
            # Extract key device information
            device_info = {
                'user_agent': user_agent,
                'ip_address': ip_address,
                'accept_language': headers.get('accept-language', ''),
                'accept_encoding': headers.get('accept-encoding', ''),
                'sec_ch_ua': headers.get('sec-ch-ua', ''),
                'sec_ch_ua_platform': headers.get('sec-ch-ua-platform', ''),
            }
            
            # Create fingerprint hash
            fingerprint_data = json.dumps(device_info, sort_keys=True)
            return hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error generating device fingerprint: {str(e)}")
            return hashlib.sha256(f"{user_agent}:{ip_address}".encode()).hexdigest()
    
    def validate_device_consistency(self, user_id: int, device_fingerprint: str, ip_address: str) -> Tuple[bool, List[str]]:
        """Validate if device is consistent with user's known devices"""
        try:
            # Get user's recent sessions
            recent_sessions = self.db.query(SecuritySession).filter(
                and_(
                    SecuritySession.user_id == user_id,
                    SecuritySession.created_at >= datetime.utcnow() - timedelta(days=30),
                    SecuritySession.session_status == SessionStatus.ACTIVE
                )
            ).all()
            
            known_devices = set()
            for session in recent_sessions:
                if session.device_fingerprint:
                    known_devices.add(session.device_fingerprint)
            
            # Check if this is a known device
            is_known_device = device_fingerprint in known_devices
            
            # Check for suspicious patterns
            risk_factors = []
            
            if not is_known_device and len(known_devices) > 0:
                risk_factors.append("NEW_DEVICE")
            
            # Check for multiple devices from same IP
            same_ip_devices = self.db.query(SecuritySession).filter(
                and_(
                    SecuritySession.user_id == user_id,
                    SecuritySession.ip_address == ip_address,
                    SecuritySession.created_at >= datetime.utcnow() - timedelta(days=7)
                )
            ).count()
            
            if same_ip_devices > 3:
                risk_factors.append("MULTIPLE_DEVICES_SAME_IP")
            
            return len(risk_factors) == 0, risk_factors
            
        except Exception as e:
            logger.error(f"Error validating device consistency: {str(e)}")
            return True, []
    
    # ==================== THREAT DETECTION ====================
    
    def calculate_suspicious_score(self, user_id: int, ip_address: str, device_fingerprint: str, 
                                 event_type: SecurityEventType, request_data: Dict[str, Any]) -> int:
        """Calculate suspicious activity score (0-100)"""
        try:
            score = 0
            
            # Check for rapid requests
            recent_requests = len([t for t in self.rate_limit_cache.get(f"{ip_address}:all", [])
                                 if (datetime.utcnow() - t).seconds < 300])
            
            if recent_requests > 20:
                score += 25
            elif recent_requests > 10:
                score += 10
            
            # Check for malicious patterns
            if self._check_malicious_patterns(request_data):
                score += 40
            
            # Check for multiple failed logins
            if user_id:
                failed_attempts = self.db.query(SecurityEvent).filter(
                    and_(
                        SecurityEvent.user_id == user_id,
                        SecurityEvent.event_type == SecurityEventType.LOGIN_FAILED,
                        SecurityEvent.created_at >= datetime.utcnow() - timedelta(hours=1)
                    )
                ).count()
                
                if failed_attempts > 5:
                    score += 30
                elif failed_attempts > 3:
                    score += 15
            
            # Check for geographic anomalies
            if self._check_geographic_anomaly(user_id, ip_address):
                score += 20
            
            return min(score, 100)
            
        except Exception as e:
            logger.error(f"Error calculating suspicious score: {str(e)}")
            return 0
    
    def _check_malicious_patterns(self, request_data: Dict[str, Any]) -> bool:
        """Check for malicious patterns in request data"""
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
    
    def _check_geographic_anomaly(self, user_id: int, ip_address: str) -> bool:
        """Check for geographic anomalies (simplified)"""
        try:
            # This is a simplified check - in production, you'd use a geolocation service
            # For now, just log the check
            logger.info(f"Geographic anomaly check for user {user_id} from IP {ip_address}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking geographic anomaly: {str(e)}")
            return False
    
    # ==================== RATE LIMITING ====================
    
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
    
    # ==================== SESSION MANAGEMENT ====================
    
    def create_security_session(self, user_id: int, user_email: str, access_token: str, 
                              device_fingerprint: str, ip_address: str, device_info: Dict[str, Any] = None,
                              location_data: Dict[str, Any] = None) -> SecuritySession:
        """Create a new security session"""
        try:
            # Generate session ID from JWT token
            session_id = hashlib.sha256(access_token.encode()).hexdigest()
            
            session = SecuritySession(
                session_id=session_id,
                user_id=user_id,
                user_email=user_email,
                access_token=access_token,
                device_fingerprint=device_fingerprint,
                ip_address=ip_address,
                device_info=device_info,
                location_data=location_data,
                expires_at=datetime.utcnow() + timedelta(hours=24),  # Default 24 hours
                created_from="LOGIN"
            )
            
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            
            return session
            
        except Exception as e:
            logger.error(f"Error creating security session: {str(e)}")
            self.db.rollback()
            return None
    
    def revoke_session(self, session_id: str, reason: str = "Manual logout") -> bool:
        """Revoke a security session"""
        try:
            session = self.db.query(SecuritySession).filter(
                SecuritySession.session_id == session_id
            ).first()
            
            if not session:
                return False
            
            session.session_status = SessionStatus.REVOKED
            session.revoked_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Revoked security session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking security session: {str(e)}")
            self.db.rollback()
            return False
    
    # ==================== EVENT LOGGING ====================
    
    def log_security_event(self, event_type: SecurityEventType, user_id: int = None, user_email: str = None,
                          ip_address: str = None, user_agent: str = None, device_fingerprint: str = None,
                          session_id: str = None, request_id: str = None, suspicious_score: int = 0,
                          risk_factors: List[str] = None, event_metadata: Dict[str, Any] = None,
                          severity: SecurityEventSeverity = SecurityEventSeverity.MEDIUM) -> SecurityEvent:
        """Log a security event"""
        try:
            event = SecurityEvent(
                event_type=event_type,
                severity=severity,
                user_id=user_id,
                user_email=user_email,
                ip_address=ip_address,
                user_agent=user_agent,
                device_fingerprint=device_fingerprint,
                session_id=session_id,
                request_id=request_id,
                suspicious_score=suspicious_score,
                risk_factors=risk_factors,
                event_metadata=event_metadata,
                created_at=datetime.utcnow()
            )
            
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            
            logger.info(f"Logged security event: {event_type.value} for user {user_id} from IP {ip_address}")
            return event
            
        except Exception as e:
            logger.error(f"Error logging security event: {str(e)}")
            self.db.rollback()
            return None
    
    # ==================== USER SECURITY MANAGEMENT ====================
    
    def update_user_security_info(self, user_id: int, ip_address: str, login_success: bool = True) -> bool:
        """Update user security information"""
        try:
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False
            
            if login_success:
                user.last_login_at = datetime.utcnow()
                user.last_login_ip = ip_address
                user.failed_login_attempts = 0
                user.account_locked_until = None
            else:
                user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
                
                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= 5:
                    user.account_locked_until = datetime.utcnow() + timedelta(hours=1)
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating user security info: {str(e)}")
            self.db.rollback()
            return False
    
    def is_account_locked(self, user_id: int) -> bool:
        """Check if user account is locked"""
        try:
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False
            
            if user.account_locked_until and user.account_locked_until > datetime.utcnow():
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking account lock status: {str(e)}")
            return False
    
    # ==================== SECURITY REPORTS ====================
    
    def get_user_security_report(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive security report for user"""
        try:
            # Get recent security events
            recent_events = self.db.query(SecurityEvent).filter(
                and_(
                    SecurityEvent.user_id == user_id,
                    SecurityEvent.created_at >= datetime.utcnow() - timedelta(days=30)
                )
            ).order_by(SecurityEvent.created_at.desc()).limit(50).all()
            
            # Get active sessions
            active_sessions = self.db.query(SecuritySession).filter(
                and_(
                    SecuritySession.user_id == user_id,
                    SecuritySession.session_status == SessionStatus.ACTIVE
                )
            ).all()
            
            # Calculate statistics
            total_events = len(recent_events)
            failed_logins = len([e for e in recent_events if e.event_type == SecurityEventType.LOGIN_FAILED])
            successful_logins = len([e for e in recent_events if e.event_type == SecurityEventType.LOGIN_SUCCESS])
            suspicious_events = len([e for e in recent_events if e.suspicious_score > 70])
            
            return {
                "user_id": user_id,
                "total_events": total_events,
                "failed_logins": failed_logins,
                "successful_logins": successful_logins,
                "suspicious_events": suspicious_events,
                "active_sessions": len(active_sessions),
                "recent_events": [self._event_to_dict(event) for event in recent_events[:10]],
                "active_sessions": [self._session_to_dict(session) for session in active_sessions]
            }
            
        except Exception as e:
            logger.error(f"Error getting security report: {str(e)}")
            return {}
    
    def _event_to_dict(self, event: SecurityEvent) -> Dict[str, Any]:
        """Convert security event to dictionary"""
        return {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "severity": event.severity.value,
            "ip_address": event.ip_address,
            "suspicious_score": event.suspicious_score,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "event_metadata": event.event_metadata
        }
    
    def _session_to_dict(self, session: SecuritySession) -> Dict[str, Any]:
        """Convert security session to dictionary"""
        return {
            "session_id": session.session_id,
            "ip_address": session.ip_address,
            "device_fingerprint": session.device_fingerprint,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "expires_at": session.expires_at.isoformat() if session.expires_at else None,
            "device_info": session.device_info
        } 