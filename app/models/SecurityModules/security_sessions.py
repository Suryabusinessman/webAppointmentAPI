from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Enum, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class SessionStatus(str, enum.Enum):
    """Session status types"""
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    SUSPICIOUS = "SUSPICIOUS"
    BLOCKED = "BLOCKED"

class SecuritySession(Base):
    """Enhanced security sessions tracking model"""
    __tablename__ = "security_sessions"
    
    # Primary key
    session_id = Column(String(255), primary_key=True)  # JWT token ID
    
    # User information
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    user_email = Column(String(255), nullable=False, index=True)
    
    # Session details
    access_token = Column(Text, nullable=False)  # JWT token
    refresh_token = Column(String(255), nullable=True)
    token_type = Column(String(50), default="bearer")
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Device and location information
    device_fingerprint = Column(String(255), nullable=False, index=True)
    device_info = Column(JSON, nullable=True)  # Browser, OS, etc.
    ip_address = Column(String(45), nullable=False, index=True)
    location_data = Column(JSON, nullable=True)  # Country, city, etc.
    
    # Security context
    session_status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False)
    suspicious_score = Column(Integer, default=0)  # 0-100
    risk_factors = Column(JSON, nullable=True)  # List of risk factors
    security_flags = Column(JSON, nullable=True)  # Security flags
    
    # Session metadata
    created_from = Column(String(100), nullable=True)  # Login method
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    activity_count = Column(Integer, default=0)  # Number of requests
    
    # Additional security data
    headers_hash = Column(String(255), nullable=True)  # Hash of request headers
    user_agent_hash = Column(String(255), nullable=True)  # Hash of user agent
    geo_location = Column(JSON, nullable=True)  # GPS coordinates if available
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="security_sessions")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_security_sessions_user_status', 'user_id', 'session_status'),
        Index('idx_security_sessions_device_ip', 'device_fingerprint', 'ip_address'),
        Index('idx_security_sessions_expires', 'expires_at'),
        Index('idx_security_sessions_activity', 'last_activity'),
    )
    
    def __repr__(self):
        return f"<SecuritySession(session_id={self.session_id}, user_id={self.user_id}, status={self.session_status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if session is active"""
        return self.session_status == SessionStatus.ACTIVE and self.expires_at > func.now()
    
    @property
    def is_suspicious(self) -> bool:
        """Check if session is suspicious"""
        return self.suspicious_score > 70 or self.session_status == SessionStatus.SUSPICIOUS 