from sqlalchemy import Column, String, BigInteger, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from models.base import Base


class WhatsAppUser(Base):
    __tablename__ = "whatsapp_users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, unique=True)
    whatsapp_phone = Column(String(20), unique=True, nullable=False, index=True)
    whatsapp_name = Column(String(255), nullable=True)
    whatsapp_profile_name = Column(String(255), nullable=True)
    is_linked = Column(Boolean, default=False)
    link_token = Column(String(255), unique=True, nullable=True, index=True)
    link_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    linked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="whatsapp_user")
    
    def __repr__(self):
        return f"<WhatsAppUser(phone={self.whatsapp_phone}, name={self.whatsapp_name})>"