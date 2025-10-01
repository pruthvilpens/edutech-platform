-- Migration to add cached AI-generated content fields to documents table
-- This prevents regenerating summary, questions, and mind maps on every request

-- Add new columns for caching AI-generated content
ALTER TABLE documents 
ADD COLUMN cached_summary TEXT,
ADD COLUMN cached_study_questions TEXT,
ADD COLUMN cached_mind_map JSONB,
ADD COLUMN summary_generated_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN questions_generated_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN mind_map_generated_at TIMESTAMP WITH TIME ZONE;

-- Add indexes for performance
CREATE INDEX idx_documents_summary_generated_at ON documents(summary_generated_at);
CREATE INDEX idx_documents_questions_generated_at ON documents(questions_generated_at);
CREATE INDEX idx_documents_mind_map_generated_at ON documents(mind_map_generated_at);