from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Enum, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class BlockType(str, enum.Enum):
    """Block types"""
    IP_BLOCK = "IP_BLOCK"
    USER_BLOCK = "USER_BLOCK"
    DEVICE_BLOCK = "DEVICE_BLOCK"
    EMAIL_BLOCK = "EMAIL_BLOCK"
    DOMAIN_BLOCK = "DOMAIN_BLOCK"

class BlockReason(str, enum.Enum):
    """Block reasons"""
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    MULTIPLE_FAILED_LOGINS = "MULTIPLE_FAILED_LOGINS"
    ACCOUNT_COMPROMISED = "ACCOUNT_COMPROMISED"
    ADMIN_BLOCK = "ADMIN_BLOCK"
    MANUAL_BLOCK = "MANUAL_BLOCK"  # Added for manual IP blocking
    AUTOMATED_BOT = "AUTOMATED_BOT"
    GEOGRAPHIC_RESTRICTION = "GEOGRAPHIC_RESTRICTION"
    MALICIOUS_ACTIVITY = "MALICIOUS_ACTIVITY"
    POLICY_VIOLATION = "POLICY_VIOLATION"

class BlockStatus(str, enum.Enum):
    """Block status"""
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    MANUAL_UNBLOCK = "MANUAL_UNBLOCK"
    AUTOMATIC_UNBLOCK = "AUTOMATIC_UNBLOCK"

class SecurityBlock(Base):
    """Security blocks management model"""
    __tablename__ = "security_blocks"
    
    # Primary key
    block_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Block details
    block_type = Column(Enum(BlockType), nullable=False, index=True)
    block_reason = Column(Enum(BlockReason), nullable=False)
    block_status = Column(Enum(BlockStatus), default=BlockStatus.ACTIVE, nullable=False)
    
    # Block target
    target_value = Column(String(255), nullable=False, index=True)  # IP, email, device fingerprint, etc.
    target_type = Column(String(50), nullable=False)  # ip, email, device, domain
    
    # User information (if applicable)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True, index=True)
    
    # Block metadata
    description = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=True)  # Evidence that led to the block
    risk_score = Column(Integer, default=0)  # 0-100 risk score
    
    # Block duration
    block_duration_hours = Column(Integer, default=24)  # Hours to block
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Block context
    created_by_system = Column(Boolean, default=True)  # True if automatic, False if manual
    created_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)  # Admin who created manual block
    
    # Additional data
    block_metadata = Column(JSON, nullable=True)  # Additional block data
    location_data = Column(JSON, nullable=True)  # Location when blocked
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    unblocked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="security_blocks")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_security_blocks_target_status', 'target_value', 'block_status'),
        Index('idx_security_blocks_type_status', 'block_type', 'block_status'),
        Index('idx_security_blocks_expires', 'expires_at'),
        Index('idx_security_blocks_user_status', 'user_id', 'block_status'),
    )
    
    def __repr__(self):
        return f"<SecurityBlock(block_id={self.block_id}, block_type={self.block_type}, target_value={self.target_value}, status={self.block_status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if block is active"""
        return self.block_status == BlockStatus.ACTIVE and self.expires_at > func.now()
    
    @property
    def is_expired(self) -> bool:
        """Check if block is expired"""
        return self.expires_at <= func.now() 