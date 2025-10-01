from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from models.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    INSTRUCTOR = "instructor" 
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="student")
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    # REMOVED: telegram_user_id column
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    # UPDATED: No more foreign_keys, added uselist=False for one-to-one
    telegram_user = relationship("TelegramUser", back_populates="user", uselist=False)
    whatsapp_user = relationship("WhatsAppUser", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User(email={self.email}, role={self.role})>"