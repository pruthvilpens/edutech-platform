Pre-Setup: System Verification
First, let's verify your WSL environment:
bash# Check your WSL version and Ubuntu version
wsl --version
lsb_release -a

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential build tools
sudo apt install -y build-essential curl git

Step 1: Project Structure Setup
bash# Create root directory
mkdir edutech-platform
cd edutech-platform

# Initialize git repository
git init
git config core.autocrlf input  # Important for WSL

# Create directory structure
mkdir -p frontend backend shared docs .github/workflows

# Create root-level files
touch README.md .gitignore .env.example docker-compose.yml
Create a professional .gitignore:
bashcat > .gitignore << 'EOF'
# Dependencies
node_modules/
.pnp
.pnp.js

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
*.env

# Build outputs
.next/
out/
build/
dist/
*.tsbuildinfo

# Python
__pycache__/
*.py[cod]
*$py.class
.Python
venv/
env/
.venv

# Database
*.db
*.sqlite
*.sqlite3

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Testing
coverage/
.pytest_cache/

# Docker
.docker/

# Misc
.vercel
.turbo
EOF

Step 2: Install Core Dependencies
Node.js (via NVM for version management)
bash# Install NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash

# Reload shell
source ~/.bashrc

# Install Node.js LTS
nvm install --lts
nvm use --lts
node --version  # Should show v20.x.x

# Install pnpm (faster than npm/yarn)
npm install -g pnpm
Python (via pyenv for version management)
bash# Install pyenv dependencies
sudo apt install -y make libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget llvm \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
  libffi-dev liblzma-dev

# Install pyenv
curl https://pyenv.run | bash

# Add to ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Reload shell
source ~/.bashrc

# Install Python 3.11
pyenv install 3.11.6
pyenv global 3.11.6
python --version  # Should show 3.11.6
Docker & Docker Compose
bash# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (avoid sudo)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Logout and login again for group changes to take effect
# Then verify
docker --version
docker compose version
PostgreSQL Client Tools
bashsudo apt install -y postgresql-client

Step 3: Frontend Setup (Next.js + TypeScript + Tailwind)
bashcd frontend

# Initialize Next.js with TypeScript
pnpm create next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# Install additional dependencies
pnpm add @tanstack/react-query zustand
pnpm add next-auth@beta
pnpm add graphql @apollo/client graphql-tag
pnpm add react-hook-form zod @hookform/resolvers
pnpm add sonner # Better toast notifications
pnpm add clsx tailwind-merge class-variance-authority

# Install dev dependencies
pnpm add -D @types/node @types/react @types/react-dom
pnpm add -D prettier prettier-plugin-tailwindcss
pnpm add -D eslint-config-prettier
pnpm add -D husky lint-staged
Configure Prettier
bashcat > .prettierrc.json << 'EOF'
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "tabWidth": 2,
  "useTabs": false,
  "printWidth": 100,
  "arrowParens": "always",
  "plugins": ["prettier-plugin-tailwindcss"]
}
EOF

cat > .prettierignore << 'EOF'
node_modules
.next
out
build
dist
*.config.js
EOF
Configure ESLint
bashcat > .eslintrc.json << 'EOF'
{
  "extends": [
    "next/core-web-vitals",
    "prettier"
  ],
  "rules": {
    "no-console": ["warn", { "allow": ["warn", "error"] }],
    "prefer-const": "error",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }]
  }
}
EOF
Update tsconfig.json
json{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
Create Proper Directory Structure
bashcd src

# Remove default files
rm -rf app/page.tsx app/globals.css

# Create organized structure
mkdir -p app/(auth)/login app/(auth)/signup
mkdir -p app/(dashboard)/admin app/(dashboard)/instructor app/(dashboard)/student
mkdir -p components/{ui,layouts,features}
mkdir -p lib/{api,utils,hooks,config}
mkdir -p types
mkdir -p styles

# Create barrel exports
touch components/index.ts
touch lib/index.ts
touch types/index.ts
Setup Tailwind with Design System
bashcat > styles/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 224.3 76.3% 48%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
EOF
Update tailwind.config.ts
typescriptimport type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};

export default config;
Install the animation plugin:
bashpnpm add tailwindcss-animate

Step 4: Backend Setup (FastAPI + Python)
bashcd ../../backend

# Create Python virtual environment
python -m venv venv
source venv/bin/activate

# Create requirements structure
mkdir -p src/{api,core,models,schemas,services,utils}
touch src/__init__.py
touch src/api/__init__.py
touch src/core/__init__.py
touch src/models/__init__.py
touch src/schemas/__init__.py
touch src/services/__init__.py
touch src/utils/__init__.py
Create requirements.txt
txt# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
psycopg2-binary==2.9.9
asyncpg==0.29.0
sqlalchemy==2.0.23

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# Document Processing
pypdf==3.17.1
python-docx==1.1.0
python-pptx==0.6.23

# NLP & AI
spacy==3.7.2
transformers==4.35.2
nltk==3.8.1
sentence-transformers==2.2.2

# Graph & Visualization
networkx==3.2.1

# Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# HTTP Client
httpx==0.25.2

# Logging & Monitoring
loguru==0.7.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2

# Code Quality
black==23.12.0
isort==5.13.2
flake8==6.1.0
mypy==1.7.1
Create requirements-dev.txt
txt-r requirements.txt

# Development
ipython==8.18.1
ipdb==0.13.13

# Testing
faker==20.1.0
factory-boy==3.3.0
Install dependencies
bashpip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Download spaCy model
python -m spacy download en_core_web_sm
Create Backend Configuration
bashcat > src/core/config.py << 'EOF'
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "EduTech Platform API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str
    
    # Hasura
    HASURA_GRAPHQL_ENDPOINT: str
    HASURA_ADMIN_SECRET: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".docx", ".txt"}
    UPLOAD_DIR: str = "uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
EOF
Create Main Application
bashcat > src/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from src.core.config import settings

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO" if not settings.DEBUG else "DEBUG",
)

# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Security Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["yourdomain.com"],
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "EduTech Platform API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs" if settings.DEBUG else "Documentation disabled in production",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
EOF
Create .env.example
bashcat > .env.example << 'EOF'
# Application
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/edutech_db

# Hasura
HASURA_GRAPHQL_ENDPOINT=http://localhost:8080/v1/graphql
HASURA_ADMIN_SECRET=your_hasura_admin_secret

# JWT
SECRET_KEY=your_secret_key_here_use_openssl_rand_hex_32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000"]
EOF

# Copy to actual .env
cp .env.example .env
Create Code Quality Tools
bash# Black configuration
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
EOF

# Flake8 configuration
cat > .flake8 << 'EOF'
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    venv,
    .venv,
    build,
    dist
EOF

Step 5: Database Setup (Postgres + Hasura)
bashcd ../..

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: edutech_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: edutech_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  hasura:
    image: hasura/graphql-engine:v2.36.0
    container_name: edutech_hasura
    restart: unless-stopped
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      HASURA_GRAPHQL_DATABASE_URL: postgres://postgres:postgres@postgres:5432/edutech_db
      HASURA_GRAPHQL_ENABLE_CONSOLE: "true"
      HASURA_GRAPHQL_DEV_MODE: "true"
      HASURA_GRAPHQL_ENABLED_LOG_TYPES: startup, http-log, webhook-log, websocket-log, query-log
      HASURA_GRAPHQL_ADMIN_SECRET: ${HASURA_ADMIN_SECRET:-myadminsecretkey}
      HASURA_GRAPHQL_UNAUTHORIZED_ROLE: anonymous
      HASURA_GRAPHQL_JWT_SECRET: '{"type":"HS256","key":"${JWT_SECRET:-your-256-bit-secret-replace-this-in-production}"}'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: edutech_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
EOF
Create Database Schema
bashmkdir -p database/migrations

cat > database/init.sql << 'EOF'
-- Enable UUID extension
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

CREATE TRIGGER update_tests_updated_at BEFORE UPDATE ON testsRetryClaude does not have the ability to run the code it generates yet.PContinueEditsql    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

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
EOF

Step 6: Start Services & Verify
bash# Start Docker services
docker compose up -d

# Wait for services to be healthy (30 seconds)
sleep 30

# Check service status
docker compose ps

# Check logs
docker compose logs postgres
docker compose logs hasura

# Test Postgres connection
psql -h localhost -U postgres -d edutech_db -c "SELECT version();"
Expected output: You should see PostgreSQL version information.
Access Hasura Console
bash# Open Hasura Console
echo "Hasura Console: http://localhost:8080"
echo "Admin Secret: myadminsecretkey"
Open your browser and navigate to http://localhost:8080. Enter the admin secret.
Track Tables in Hasura
In the Hasura Console:

Go to Data tab
Click Track All to track all tables
Click Track All under Foreign Keys
Go to Relationships and verify they're auto-created


Step 7: Setup Git Hooks (Husky)
bashcd frontend

# Initialize Husky
pnpm exec husky init

# Create pre-commit hook
cat > .husky/pre-commit << 'EOF'
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

pnpm lint-staged
EOF

chmod +x .husky/pre-commit

# Add lint-staged configuration
cat >> package.json << 'EOF'
,
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md,yml,yaml}": [
      "prettier --write"
    ]
  }
EOF

Step 8: Create Shared Types
bashcd ../shared
mkdir -p types

cat > types/index.ts << 'EOF'
// User Types
export enum UserRole {
  ADMIN = 'admin',
  INSTRUCTOR = 'instructor',
  STUDENT = 'student',
}

export interface User {
  id: string;
  email: string;
  fullName: string;
  role: UserRole;
  isActive: boolean;
  emailVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

// Document Types
export enum DocumentStatus {
  UPLOADED = 'uploaded',
  PROCESSING = 'processing',
  PROCESSED = 'processed',
  FAILED = 'failed',
}

export interface Document {
  id: string;
  uploadedBy: string;
  originalFilename: string;
  filePath: string;
  fileSize: number;
  mimeType: string;
  status: DocumentStatus;
  metadata: Record<string, any>;
  createdAt: string;
  processedAt?: string;
}

// Question Types
export interface Question {
  id: string;
  documentId?: string;
  createdBy: string;
  questionText: string;
  questionType: string;
  options: string[];
  correctAnswer: string;
  explanation?: string;
  difficulty: 'easy' | 'medium' | 'hard';
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

// Test Types
export enum TestStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
}

export interface Test {
  id: string;
  createdBy: string;
  title: string;
  description?: string;
  status: TestStatus;
  durationMinutes?: number;
  totalMarks: number;
  passingMarks: number;
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  publishedAt?: string;
}

// Result Types
export interface Result {
  id: string;
  testId: string;
  userId: string;
  score: number;
  totalMarks: number;
  percentage: number;
  timeTakenSeconds: number;
  answers: Record<string, any>;
  submittedAt: string;
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
EOF

cat > types/package.json << 'EOF'
{
  "name": "@edutech/shared",
  "version": "1.0.0",
  "main": "types/index.ts",
  "types": "types/index.ts"
}
EOF

Step 9: Create Root-Level Documentation
bashcd ..

cat > README.md << 'EOF'
# EduTech Platform

A comprehensive educational technology platform with AI-powered document processing, test management, and analytics.

## 🏗️ Architecture
edutech-platform/
├── frontend/          # Next.js 14 + TypeScript + Tailwind
├── backend/           # FastAPI + Python
├── shared/            # Shared TypeScript types
├── database/          # PostgreSQL schemas & migrations
├── docs/              # Documentation
└── docker-compose.yml # Docker orchestration

## 🚀 Quick Start

### Prerequisites

- Node.js 20+ (via nvm)
- Python 3.11+ (via pyenv)
- Docker & Docker Compose
- PostgreSQL Client Tools

### Installation

1. **Clone and setup:**
```bash
   git clone <repository-url>
   cd edutech-platform

Start infrastructure:

bash   docker compose up -d

Setup Frontend:

bash   cd frontend
   pnpm install
   cp .env.example .env
   pnpm dev

Setup Backend:

bash   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   python src/main.py
Access Points

Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Docs: http://localhost:8000/api/docs
Hasura Console: http://localhost:8080
PostgreSQL: localhost:5432

Default Credentials

Admin: admin@edutech.com / Admin@123
Hasura Secret: myadminsecretkey

📦 Tech Stack
Frontend

Next.js 14 (App Router)
TypeScript
Tailwind CSS
React Query
Zustand
NextAuth.js

Backend

FastAPI
PostgreSQL
Hasura GraphQL
Redis
SQLAlchemy

AI/ML

spaCy
Transformers
NLTK
NetworkX

Infrastructure

Docker & Docker Compose
Vercel (Frontend)
Railway/Render (Backend)

🛠️ Development
Code Quality
Frontend:
bashcd frontend
pnpm lint        # ESLint
pnpm format      # Prettier
pnpm type-check  # TypeScript
Backend:
bashcd backend
source venv/bin/activate
black src/       # Format
isort src/       # Sort imports
flake8 src/      # Lint
mypy src/        # Type check
Testing
Frontend:
bashpnpm test        # Jest
pnpm test:e2e    # Playwright
Backend:
bashpytest           # All tests
pytest --cov     # With coverage
📚 Documentation

Architecture
API Documentation
Database Schema
Deployment Guide

🤝 Contributing

Create a feature branch
Make your changes
Run tests and linters
Submit a pull request

📄 License
Proprietary - All rights reserved
👥 Team

Development Team: [Your Team]
Contact: [contact@edutech.com]
EOF

Create documentation structure
mkdir -p docs
cat > docs/architecture.md << 'EOF'
Architecture Overview
System Design
The EduTech Platform follows a microservices architecture with clear separation of concerns.
Components

Frontend (Next.js)

Server-side rendering
API routes for BFF pattern
Client-side state management


Backend (FastAPI)

RESTful API
Document processing
AI/ML services


Hasura GraphQL

Real-time subscriptions
Role-based access control
Database abstraction


PostgreSQL

Primary data store
JSONB for flexible schemas


Redis

Session storage
Rate limiting
Caching layer



Data Flow
User → Next.js → Hasura GraphQL → PostgreSQL
                ↓
            FastAPI (AI Processing)
                ↓
            PostgreSQL (Results)
Security

JWT-based authentication
Role-based access control (RBAC)
Row-level security in Hasura
Rate limiting
Input validation at all layers
EOF


---

## **Step 10: Create Environment Files**
```bash
# Frontend environment
cd frontend

cat > .env.local << 'EOF'
# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Hasura
NEXT_PUBLIC_HASURA_GRAPHQL_URL=http://localhost:8080/v1/graphql
HASURA_GRAPHQL_ADMIN_SECRET=myadminsecretkey

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-change-in-production

# JWT
JWT_SECRET=your-256-bit-secret-replace-this-in-production
EOF

# Backend environment
cd ../backend

cat > .env << 'EOF'
# Application
DEBUG=true

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/edutech_db

# Hasura
HASURA_GRAPHQL_ENDPOINT=http://localhost:8080/v1/graphql
HASURA_ADMIN_SECRET=myadminsecretkey

# JWT
SECRET_KEY=your-secret-key-here-use-openssl-rand_hex_32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000"]
EOF

Step 11: Test Everything
Test Backend
bashcd backend
source venv/bin/activate
python src/main.py
In another terminal:
bashcurl http://localhost:8000/health
Expected response:
json{
  "status": "healthy",
  "app": "EduTech Platform API",
  "version": "1.0.0"
}
Test Frontend
bashcd frontend
pnpm dev
Visit http://localhost:3000 - you should see the Next.js default page.
Test Database
bashpsql -h localhost -U postgres -d edutech_db -c "SELECT COUNT(*) FROM users;"
Expected output: count: 1 (the admin user)

Step 12: Create Utility Scripts
bashcd ..
mkdir -p scripts

cat > scripts/dev.sh << 'EOF'
#!/bin/bash
# Development startup script

echo "🚀 Starting EduTech Platform Development Environment..."

# Start Docker services
echo "📦 Starting Docker services..."
docker compose up -d

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 10

# Start Backend
echo "🐍 Starting Backend..."
cd backend
source venv/bin/activate
python src/main.py &
BACKEND_PID=$!

# Start Frontend
echo "⚛️  Starting Frontend..."
cd ../frontend
pnpm dev &
FRONTEND_PID=$!

echo "✅ Development environment ready!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "Hasura: http://localhost:8080"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; docker compose down; exit" INT
wait
EOF

chmod +x scripts/dev.sh

cat > scripts/reset-db.sh << 'EOF'
#!/bin/bash
# Reset database script

echo "⚠️  This will reset the database. Are you sure? (yes/no)"
read confirmation

if [ "$confirmation" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo "🗑️  Resetting database..."

docker compose down -v
docker compose up -d postgres

echo "⏳ Waiting for PostgreSQL..."
sleep 10

docker compose up -d hasura

echo "✅ Database reset complete!"
EOF

chmod +x scripts/reset-db.sh

cat > scripts/setup.sh << 'EOF'
#!/bin/bash
# Initial setup script

echo "🎯 Setting up EduTech Platform..."

# Check prerequisites
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }
command -v python >/dev/null 2>&1 || { echo "❌ Python is required but not installed."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }

echo "✅ Prerequisites check passed"

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
pnpm install

# Setup backend
echo "🐍 Setting up backend..."
cd ../backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Start Docker services
echo "🐳 Starting Docker services..."
cd ..
docker compose up -d

echo "✅ Setup complete!"
echo "Run './scripts/dev.sh' to start development environment"
EOF

chmod +x scripts/setup.sh