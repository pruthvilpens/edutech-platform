This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.




GUIDE:

 Prerequisites

  - Docker & Docker Compose (required)
  - Node.js 18+ with pnpm package manager
  - Python 3.11+ with pip
  - Git

  Setup Instructions

  1. Clone the Repository

  git clone https://github.com/pruthvilpens/edutech-platform.git
  cd edutech-platform

  2. Environment Configuration

  # Copy environment files
  cp .env.example .env
  cp backend/.env.example backend/.env

  Edit the .env files with your actual values:
  - Set strong passwords and secret keys
  - Configure JWT secrets
  - Set CORS origins if needed

  3. Database & Services Setup (Docker)

  # Start all services (PostgreSQL, Hasura, Redis)
  docker-compose up -d

  # Wait for services to be ready (check with)
  docker-compose ps

  Services will be available at:
  - PostgreSQL: localhost:5432
  - Hasura Console: http://localhost:8081
  - Redis: localhost:6380

  4. Backend Setup

  cd backend

  # Create virtual environment
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate

  # Install dependencies
  pip install -r requirements.txt

  # Run backend server
  uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

  Backend will be available at: http://localhost:8000

  5. Frontend Setup

  cd frontend

  # Install dependencies
  pnpm install

  # Run development server
  pnpm dev

  Frontend will be available at: http://localhost:3000

  Default Access

  - Admin Login: admin@edutech.com / Admin@123
  - Hasura Console: http://localhost:8081 (admin secret from .env)       

  Key Features Available

  - User authentication (admin/instructor/student roles)
  - RBAC (Role-Based Access Control)

  Troubleshooting

  - Ensure Docker services are healthy: docker-compose ps
  - Check logs: docker-compose logs [service-name]
  - Verify port availability (3000, 8000, 5432, 8081, 6380)
  - Check environment variables are properly set