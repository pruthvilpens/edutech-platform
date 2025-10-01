from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from uuid import UUID
import asyncio

from utils.database import get_db_session
from utils.auth import get_current_user
from models.user import User, UserRole
from models.document import Document, DocumentChatSession, ChatMessage, DocumentStatus
from schemas.document import (
    DocumentResponse, DocumentListResponse, ChatMessageCreate, 
    ChatResponse, ChatSessionResponse, DocumentSummaryResponse,
    StudyQuestionsResponse
)
from services.document_service import document_service
from services.gemini_service import gemini_service
from core.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])
security = HTTPBearer()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Upload a document (instructors only)"""
    # Check if user is instructor or admin
    if current_user.role not in [UserRole.INSTRUCTOR.value, UserRole.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Only instructors can upload documents")
    
    # Validate file
    if not document_service.validate_file_type(file.filename):
        raise HTTPException(
            status_code=400, 
            detail=f"File type not supported. Allowed types: {list(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    if not document_service.validate_file_size(file_size):
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    try:
        # Save file
        file_path = await document_service.save_uploaded_file(file_content, file.filename)
        mime_type = document_service.get_mime_type(file.filename)
        
        # Create document record
        document = Document(
            uploaded_by=current_user.id,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        # Start background processing with new database session
        asyncio.create_task(document_service.process_document_async(str(document.id)))
        
        return document
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """List documents based on user role"""
    offset = (page - 1) * per_page
    
    # Build query based on user role
    query = select(Document)
    
    if current_user.role == UserRole.STUDENT.value:
        # Students can only see processed documents
        query = query.where(Document.status == DocumentStatus.processed)
    elif current_user.role == UserRole.INSTRUCTOR.value:
        # Instructors can see their own documents and processed documents from others
        query = query.where(
            or_(
                Document.uploaded_by == current_user.id,
                Document.status == DocumentStatus.processed
            )
        )
    # Admins can see all documents (no additional filter)
    
    if status:
        query = query.where(Document.status == status)
    
    # Get total count
    count_result = await db.execute(query)
    total = len(count_result.fetchall())
    
    # Get paginated results
    result = await db.execute(
        query.order_by(Document.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    documents = result.scalars().all()
    
    return DocumentListResponse(
        documents=documents,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Get document details"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    if current_user.role == UserRole.STUDENT.value and document.status != DocumentStatus.processed:
        raise HTTPException(status_code=403, detail="Document not available")
    
    if (current_user.role == UserRole.INSTRUCTOR.value and 
        document.uploaded_by != current_user.id and 
        document.status != DocumentStatus.processed):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return document


@router.post("/{document_id}/chat", response_model=ChatResponse)
async def chat_with_document(
    document_id: UUID,
    message_data: ChatMessageCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Start or continue chat with document"""
    # Get document
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != DocumentStatus.processed:
        raise HTTPException(status_code=400, detail="Document not ready for chat")
    
    # Check if user has access
    if current_user.role == UserRole.STUDENT.value or document.uploaded_by == current_user.id:
        # Students and document owners can chat
        pass
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get or create chat session
        session_result = await db.execute(
            select(DocumentChatSession).where(
                and_(
                    DocumentChatSession.document_id == document_id,
                    DocumentChatSession.user_id == current_user.id
                )
            )
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            session = DocumentChatSession(
                document_id=document_id,
                user_id=current_user.id,
                session_name=f"Chat with {document.original_filename}"
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
        
        # Save user message
        user_message = ChatMessage(
            session_id=session.id,
            role="user",
            content=message_data.content
        )
        db.add(user_message)
        await db.commit()
        await db.refresh(user_message)
        
        # Get chat history
        history_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(20)
        )
        chat_history = [
            {"role": msg.role, "content": msg.content} 
            for msg in reversed(history_result.scalars().all()[:-1])  # Exclude current message
        ]
        
        # Get AI response
        ai_response_data = await gemini_service.chat_with_document(
            document.processed_text,
            message_data.content,
            chat_history
        )
        
        # Save AI response
        ai_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=ai_response_data["response"],
            message_metadata={"model_used": ai_response_data.get("model_used", "unknown")}
        )
        db.add(ai_message)
        await db.commit()
        await db.refresh(ai_message)
        
        return ChatResponse(
            message=user_message,
            ai_response=ai_message
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/{document_id}/chat/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    document_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Get chat sessions for a document"""
    # Check document access
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get user's chat sessions
    # Get sessions with proper SQLAlchemy relationship loading
    from sqlalchemy.orm import selectinload
    
    sessions_result = await db.execute(
        select(DocumentChatSession)
        .options(selectinload(DocumentChatSession.messages))
        .where(
            and_(
                DocumentChatSession.document_id == document_id,
                DocumentChatSession.user_id == current_user.id
            )
        )
        .order_by(DocumentChatSession.updated_at.desc())
    )
    
    sessions = sessions_result.scalars().all()
    return sessions


@router.get("/{document_id}/summary", response_model=DocumentSummaryResponse)
async def get_document_summary(
    document_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Get AI-generated summary of document (cached if available)"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != DocumentStatus.processed:
        raise HTTPException(status_code=400, detail="Document not ready")
    
    # Check if we have a cached summary
    if document.cached_summary and document.summary_generated_at:
        return DocumentSummaryResponse(
            summary=document.cached_summary,
            success=True
        )
    
    # Generate new summary and cache it
    summary_data = await gemini_service.extract_document_summary(document.processed_text)
    
    if summary_data["success"]:
        # Cache the summary
        from datetime import datetime
        document.cached_summary = summary_data["summary"]
        document.summary_generated_at = datetime.utcnow()
        await db.commit()
    
    return DocumentSummaryResponse(**summary_data)


@router.get("/{document_id}/study-questions", response_model=StudyQuestionsResponse)
async def get_study_questions(
    document_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Get AI-generated study questions for document (cached if available)"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != DocumentStatus.processed:
        raise HTTPException(status_code=400, detail="Document not ready")
    
    # Check if we have cached study questions
    if document.cached_study_questions and document.questions_generated_at:
        return StudyQuestionsResponse(
            questions=document.cached_study_questions,
            success=True
        )
    
    # Generate new questions and cache them
    questions_data = await gemini_service.suggest_study_questions(document.processed_text)
    
    if questions_data["success"]:
        # Cache the questions
        from datetime import datetime
        document.cached_study_questions = questions_data["questions"]
        document.questions_generated_at = datetime.utcnow()
        await db.commit()
    
    return StudyQuestionsResponse(**questions_data)


@router.get("/{document_id}/mind-map", response_model=dict)
async def get_document_mind_map(
    document_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Generate mind map for document (cached if available)"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Students can only access processed documents from instructors or their own
    if (current_user.role == UserRole.STUDENT.value and 
        document.uploaded_by != current_user.id and 
        document.status != DocumentStatus.processed):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if document is processed
    if document.status != DocumentStatus.processed:
        raise HTTPException(status_code=400, detail="Document not ready")
    
    # Check if we have a cached mind map
    if document.cached_mind_map and document.mind_map_generated_at:
        return {
            "mind_map": document.cached_mind_map,
            "success": True
        }
    
    # Generate new mind map and cache it
    mind_map_data = await gemini_service.generate_mind_map(document.processed_text)
    
    if mind_map_data["success"]:
        # Cache the mind map
        from datetime import datetime
        document.cached_mind_map = mind_map_data["mind_map"]
        document.mind_map_generated_at = datetime.utcnow()
        await db.commit()
    
    return mind_map_data


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Delete document (owner or admin only)"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    if (current_user.role != UserRole.ADMIN.value and 
        document.uploaded_by != current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Delete file from disk
        import os
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database (cascade will handle related records)
        await db.delete(document)
        await db.commit()
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")