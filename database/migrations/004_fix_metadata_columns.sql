-- Fix metadata column conflicts with SQLAlchemy

-- Update documents table
ALTER TABLE documents RENAME COLUMN metadata TO file_metadata;

-- Update chat_messages table  
ALTER TABLE chat_messages RENAME COLUMN metadata TO message_metadata;