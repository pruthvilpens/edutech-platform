import os
import aiofiles
from pathlib import Path
from typing import Optional, Dict, Any
import mimetypes
from loguru import logger
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Document processing imports
import pypdf
from docx import Document as DocxDocument
import nltk
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.document import Document, DocumentStatus
from core.config import settings
from utils.database import get_db_session


class DocumentProcessingService:
    def __init__(self):
        # Make upload directory absolute to avoid path issues
        if os.path.isabs(settings.UPLOAD_DIR):
            self.upload_dir = Path(settings.UPLOAD_DIR)
        else:
            # Create uploads directory relative to the project root (backend directory)
            project_root = Path(__file__).parent.parent.parent
            self.upload_dir = project_root / settings.UPLOAD_DIR
        
        self.upload_dir.mkdir(exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Ensure NLTK data is available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to disk and return file path"""
        # Generate unique filename
        file_extension = Path(filename).suffix
        unique_filename = f"{hash(filename + str(len(file_content)))}{file_extension}"
        file_path = self.upload_dir / unique_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return str(file_path)
    
    def _resolve_file_path(self, file_path: str) -> str:
        """Resolve file path to absolute path"""
        path_obj = Path(file_path)
        if path_obj.is_absolute():
            return file_path
        else:
            # If relative and starts with 'uploads/', it's relative to project root
            if file_path.startswith('uploads/'):
                # Remove 'uploads/' prefix and use just the filename
                filename = file_path[8:]  # Remove 'uploads/' prefix
                return str(self.upload_dir / filename)
            else:
                # Otherwise, assume it's relative to the upload directory
                return str(self.upload_dir / file_path)
    
    async def extract_text_from_file(self, file_path: str, mime_type: str) -> Optional[str]:
        """Extract text content from uploaded file"""
        try:
            # Resolve the file path to handle both absolute and relative paths
            resolved_path = self._resolve_file_path(file_path)
            
            loop = asyncio.get_event_loop()
            
            if mime_type == "application/pdf":
                text = await loop.run_in_executor(
                    self.executor,
                    self._extract_pdf_text,
                    resolved_path
                )
            elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = await loop.run_in_executor(
                    self.executor,
                    self._extract_docx_text,
                    resolved_path
                )
            elif mime_type == "text/plain":
                async with aiofiles.open(resolved_path, 'r', encoding='utf-8') as f:
                    text = await f.read()
            else:
                logger.warning(f"Unsupported file type: {mime_type}")
                return None
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from {resolved_path}: {str(e)}")
            return None
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file (synchronous)"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file (synchronous)"""
        doc = DocxDocument(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    
    async def process_document(self, db: AsyncSession, document_id: str) -> bool:
        """Process document: extract text and update status"""
        try:
            # Get document from database
            result = await db.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()
            
            if not document:
                logger.error(f"Document {document_id} not found")
                return False
            
            # Update status to processing
            document.status = DocumentStatus.processing
            await db.commit()
            
            # Extract text
            extracted_text = await self.extract_text_from_file(
                document.file_path, 
                document.mime_type
            )
            
            if extracted_text:
                # Clean and process text
                processed_text = await self._clean_text(extracted_text)
                
                # Update document with extracted text
                document.raw_text = extracted_text
                document.processed_text = processed_text
                document.status = DocumentStatus.processed
                document.processed_at = datetime.utcnow()
                
                # Add metadata
                document.file_metadata = {
                    "word_count": len(processed_text.split()),
                    "character_count": len(processed_text),
                    "extraction_successful": True
                }
            else:
                document.status = DocumentStatus.failed
                document.file_metadata = {"extraction_error": "Failed to extract text"}
            
            await db.commit()
            return document.status == DocumentStatus.processed
            
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {str(e)}")
            # Update status to failed
            try:
                result = await db.execute(
                    select(Document).where(Document.id == document_id)
                )
                document = result.scalar_one_or_none()
                if document:
                    document.status = DocumentStatus.failed
                    document.file_metadata = {"processing_error": str(e)}
                    await db.commit()
            except:
                pass
            return False
    
    async def process_document_async(self, document_id: str) -> bool:
        """Process document with its own database session"""
        async for db in get_db_session():
            try:
                return await self.process_document(db, document_id)
            finally:
                await db.close()
    
    async def _clean_text(self, text: str) -> str:
        """Clean and preprocess extracted text"""
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Remove very long repeated characters (likely artifacts)
        import re
        text = re.sub(r'(.)\1{10,}', r'\1', text)
        
        return text
    
    def get_mime_type(self, filename: str) -> Optional[str]:
        """Get MIME type from filename"""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type
    
    def validate_file_type(self, filename: str) -> bool:
        """Validate if file type is supported"""
        extension = Path(filename).suffix.lower()
        return extension in settings.ALLOWED_EXTENSIONS
    
    def validate_file_size(self, file_size: int) -> bool:
        """Validate file size"""
        return file_size <= settings.MAX_FILE_SIZE


# Global instance
document_service = DocumentProcessingService()