
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE user_role AS ENUM ('admin', 'instructor', 'student');
CREATE TYPE document_status AS ENUM ('uploaded', 'processing', 'processed', 'failed');
CREATE TYPE test_status AS ENUM ('draft', 'published', 'archived');

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'student',
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- RBAC: Role Master
CREATE TABLE rolemaster (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- RBAC: Permission Master
CREATE TABLE permissionmaster (
    permission_id SERIAL PRIMARY KEY,
    permission_name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- RBAC: Menu Master
CREATE TABLE menumaster (
    menu_id SERIAL PRIMARY KEY,
    menu_name VARCHAR(100) NOT NULL,
    menu_path VARCHAR(255) NOT NULL,
    parent_id INTEGER REFERENCES menumaster(menu_id),
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- RBAC: User-Role Mapping
CREATE TABLE usermaster (
    user_role_id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES rolemaster(role_id),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id)
);

-- RBAC: Role-Menu-Permission Mapping
CREATE TABLE rolemenupermissionmapping (
    mapping_id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES rolemaster(role_id) ON DELETE CASCADE,
    menu_id INTEGER REFERENCES menumaster(menu_id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissionmaster(permission_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, menu_id, permission_id)
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    status document_status DEFAULT 'uploaded',
    raw_text TEXT,
    processed_text TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Questions table
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) DEFAULT 'mcq',
    options JSONB DEFAULT '[]',
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    difficulty VARCHAR(20) DEFAULT 'medium',
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tests table
CREATE TABLE tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status test_status DEFAULT 'draft',
    duration_minutes INTEGER,
    total_marks INTEGER DEFAULT 0,
    passing_marks INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE
);

-- Test Questions (many-to-many)
CREATE TABLE test_questions (
    test_id UUID REFERENCES tests(id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    marks INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    PRIMARY KEY (test_id, question_id)
);

-- Test Assignments
CREATE TABLE test_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_id UUID REFERENCES tests(id) ON DELETE CASCADE,
    assigned_to UUID REFERENCES users(id) ON DELETE CASCADE,
    assigned_by UUID REFERENCES users(id) ON DELETE SET NULL,
    due_date TIMESTAMP WITH TIME ZONE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(test_id, assigned_to)
);

-- Test Results
CREATE TABLE results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_id UUID REFERENCES tests(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    score DECIMAL(5,2),
    total_marks INTEGER,
    percentage DECIMAL(5,2),
    time_taken_seconds INTEGER,
    answers JSONB DEFAULT '{}',
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(test_id, user_id)
);


-- Mind Maps
CREATE TABLE mindmaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    map_data JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Flashcards
CREATE TABLE flashcards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'medium',
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Leaderboards
CREATE TABLE leaderboards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    total_score INTEGER DEFAULT 0,
    tests_completed INTEGER DEFAULT 0,
    average_percentage DECIMAL(5,2) DEFAULT 0,
    rank INTEGER,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_questions_document_id ON questions(document_id);
CREATE INDEX idx_questions_created_by ON questions(created_by);
CREATE INDEX idx_tests_created_by ON tests(created_by);
CREATE INDEX idx_tests_status ON tests(status);
CREATE INDEX idx_results_test_id ON results(test_id);
CREATE INDEX idx_results_user_id ON results(user_id);
CREATE INDEX idx_leaderboards_rank ON leaderboards(rank);

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_questions_updated_at BEFORE UPDATE ON questions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tests_updated_at BEFORE UPDATE ON tests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mindmaps_updated_at BEFORE UPDATE ON mindmaps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default roles
INSERT INTO rolemaster (role_name, description) VALUES
    ('admin', 'Full system access'),
    ('instructor', 'Can create and manage courses, tests, and view student results'),
    ('student', 'Can take tests and view own results');

-- Insert default permissions
INSERT INTO permissionmaster (permission_name, resource, action, description) VALUES
    ('user.create', 'user', 'create', 'Create new users'),
    ('user.read', 'user', 'read', 'View user details'),
    ('user.update', 'user', 'update', 'Update user information'),
    ('user.delete', 'user', 'delete', 'Delete users'),
    ('document.create', 'document', 'create', 'Upload documents'),
    ('document.read', 'document', 'read', 'View documents'),
    ('document.delete', 'document', 'delete', 'Delete documents'),
    ('question.create', 'question', 'create', 'Create questions'),
    ('question.read', 'question', 'read', 'View questions'),
    ('question.update', 'question', 'update', 'Update questions'),
    ('question.delete', 'question', 'delete', 'Delete questions'),
    ('test.create', 'test', 'create', 'Create tests'),
    ('test.read', 'test', 'read', 'View tests'),
    ('test.update', 'test', 'update', 'Update tests'),
    ('test.delete', 'test', 'delete', 'Delete tests'),
    ('test.assign', 'test', 'assign', 'Assign tests to students'),
    ('result.read', 'result', 'read', 'View results'),
    ('result.read_all', 'result', 'read_all', 'View all student results');

-- Insert default menus
INSERT INTO menumaster (menu_name, menu_path, parent_id, icon, sort_order) VALUES
    ('Dashboard', '/dashboard', NULL, 'home', 1),
    ('Users', '/users', NULL, 'users', 2),
    ('Documents', '/documents', NULL, 'file-text', 3),
    ('Questions', '/questions', NULL, 'help-circle', 4),
    ('Tests', '/tests', NULL, 'clipboard', 5),
    ('Results', '/results', NULL, 'bar-chart', 6),
    ('Mind Maps', '/mindmaps', NULL, 'share-2', 7),
    ('Flashcards', '/flashcards', NULL, 'layers', 8),
    ('Leaderboard', '/leaderboard', NULL, 'trophy', 9);

-- Create admin user (password: Admin@123 - hashed with bcrypt)
INSERT INTO users (email, password_hash, full_name, role, email_verified) VALUES
    ('admin@edutech.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7h5ryHONNe', 'System Admin', 'admin', true);
