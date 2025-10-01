-- Migration for document chat functionality
-- Add chat session and message tables

-- Document Chat Sessions table
CREATE TABLE document_chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    session_name VARCHAR(255) DEFAULT 'Chat Session',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chat Messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES document_chat_sessions(id) ON DELETE CASCADE NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_chat_sessions_document_id ON document_chat_sessions(document_id);
CREATE INDEX idx_chat_sessions_user_id ON document_chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_updated_at ON document_chat_sessions(updated_at);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);

-- Update trigger for chat sessions
CREATE TRIGGER update_chat_sessions_updated_at 
    BEFORE UPDATE ON document_chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add constraint to ensure unique session per user per document
CREATE UNIQUE INDEX idx_unique_user_document_session 
    ON document_chat_sessions(document_id, user_id);