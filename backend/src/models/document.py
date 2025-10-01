from sqlalchemy import Column, String, Text, BigInteger, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from models.base import Base


class DocumentStatus(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100))
    status = Column(SQLEnum(DocumentStatus, name="document_status"), default=DocumentStatus.uploaded)
    raw_text = Column(Text)
    processed_text = Column(Text)
    file_metadata = Column(JSONB, default=dict)
    
    # Cached AI-generated content
    cached_summary = Column(Text)
    cached_study_questions = Column(Text)
    cached_mind_map = Column(JSONB)
    summary_generated_at = Column(DateTime(timezone=True))
    questions_generated_at = Column(DateTime(timezone=True))
    mind_map_generated_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    uploader = relationship("User", backref="uploaded_documents")
    chat_sessions = relationship("DocumentChatSession", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(filename={self.original_filename}, status={self.status})>"


class DocumentChatSession(Base):
    __tablename__ = "document_chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_name = Column(String(255), default="Chat Session")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chat_sessions")
    user = relationship("User", backref="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DocumentChatSession(id={self.id}, document={self.document_id})>"


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("document_chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    message_metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("DocumentChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(role={self.role}, session={self.session_id})>"