from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class DocumentUpload(BaseModel):
    original_filename: str
    file_size: int
    mime_type: Optional[str] = None


class DocumentResponse(BaseModel):
    id: UUID
    uploaded_by: Optional[UUID]
    original_filename: str
    file_path: str
    file_size: int
    mime_type: Optional[str]
    status: str
    file_metadata: Dict[str, Any] = {}
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    per_page: int


class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    message_metadata: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    id: UUID
    document_id: UUID
    user_id: UUID
    session_name: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    message: ChatMessageResponse
    ai_response: ChatMessageResponse


class DocumentSummaryResponse(BaseModel):
    summary: str
    success: bool
    
    
class StudyQuestionsResponse(BaseModel):
    questions: str
    success: bool