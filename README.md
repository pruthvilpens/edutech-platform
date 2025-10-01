
  How to Run the Yeebitz Platform (After Cloning)

  Prerequisites

  - Docker & Docker Compose
  - Node.js 18+ with pnpm
  - Python 3.11+ with pip
  - Git

  Step 1: Clone the Repository

  git clone https://github.com/pruthvilpens/edutech-platform.git
  cd edutech-platform

  Step 2: Environment Configuration

  # Copy environment files
  cp .env.example .env

  # Edit .env file with your actual values:
  # - Set strong SECRET_KEY and NEXTAUTH_SECRET
  # - Configure GEMINI_API_KEY if using AI features
  # - Set TELEGRAM_BOT_TOKEN if using Telegram integration

  Step 3: Start Database & Services (Docker)

  # Start PostgreSQL, Hasura, and Redis
  docker-compose up -d

  # Verify services are running
  docker-compose ps

  Services will be available at:
  - PostgreSQL: localhost:5432
  - Hasura Console: http://localhost:8081
  - Redis: localhost:6380

  Step 4: Backend Setup

  cd backend

  # Create virtual environment
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate

  # Install dependencies
  pip install -r requirements.txt

  # Start backend server
  uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

  Backend will be available at: http://localhost:8000

  Step 5: Frontend Setup (New Terminal)

  cd frontend

  # Install dependencies
  pnpm install

  # Start development server
  pnpm dev

  Frontend will be available at: http://localhost:3000

  Default Access

  - Admin Login: admin@edutech.com / Admin@123
  - Hasura Console: http://localhost:8081 (admin secret: myadminsecretkey)       

  Key Features Available

  - User authentication (admin/instructor/student roles)
  - Document upload and AI-powered analysis
  - WhatsApp & Telegram bot integration
  - Role-Based Access Control (RBAC)

  Troubleshooting

  - Check Docker services: docker-compose ps
  - View logs: docker-compose logs [service-name]
  - Ensure ports are available: 3000, 8000, 5432, 8081, 6380
  - Verify environment variables are set correctly
