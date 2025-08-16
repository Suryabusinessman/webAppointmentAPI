from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class SecurityEventType(str, enum.Enum):
    """Security event types"""
    LOGIN_ATTEMPT = "LOGIN_ATTEMPT"
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    REGISTRATION = "REGISTRATION"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    PASSWORD_RESET = "PASSWORD_RESET"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    ACCOUNT_UNLOCKED = "ACCOUNT_UNLOCKED"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    IP_BLOCKED = "IP_BLOCKED"
    IP_UNBLOCKED = "IP_UNBLOCKED"
    DEVICE_CHANGE = "DEVICE_CHANGE"
    LOCATION_CHANGE = "LOCATION_CHANGE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    TOKEN_REFRESH = "TOKEN_REFRESH"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    SESSION_CREATED = "SESSION_CREATED"
    SESSION_DESTROYED = "SESSION_DESTROYED"
    API_ACCESS = "API_ACCESS"

class SecurityEventSeverity(str, enum.Enum):
    """Security event severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SecurityEvent(Base):
    """Security events tracking model"""
    __tablename__ = "security_events"
    
    # Primary key
    event_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Event details
    event_type = Column(Enum(SecurityEventType), nullable=False, index=True)
    severity = Column(Enum(SecurityEventSeverity), nullable=False, default=SecurityEventSeverity.MEDIUM)
    description = Column(Text, nullable=True)
    
    # User information
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True, index=True)
    
    # Request information
    ip_address = Column(String(45), nullable=False, index=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    device_fingerprint = Column(String(255), nullable=True, index=True)
    location_data = Column(JSON, nullable=True)  # Country, city, etc.
    
    # Session information
    session_id = Column(String(255), nullable=True, index=True)
    request_id = Column(String(255), nullable=True, index=True)
    
    # Security context
    suspicious_score = Column(Integer, default=0)  # 0-100
    risk_factors = Column(JSON, nullable=True)  # List of risk factors
    mitigation_applied = Column(JSON, nullable=True)  # Actions taken
    
    # Additional data
    event_metadata = Column(JSON, nullable=True)  # Additional event data
    headers = Column(JSON, nullable=True)  # Request headers (sanitized)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="security_events")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_security_events_user_ip', 'user_id', 'ip_address'),
        Index('idx_security_events_type_created', 'event_type', 'created_at'),
        Index('idx_security_events_severity_created', 'severity', 'created_at'),
    )
    
    def __repr__(self):
        return f"<SecurityEvent(event_id={self.event_id}, event_type={self.event_type}, user_id={self.user_id}, ip_address={self.ip_address})>" 