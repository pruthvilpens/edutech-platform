#!/bin/bash

# Production startup script for EduTech Platform API

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting YeeBitz Platform API...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run setup first.${NC}"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Using environment variables.${NC}"
fi

# Install/update dependencies
echo -e "${GREEN}📦 Installing dependencies...${NC}"
pip install -r requirements.txt

# Run database migrations if needed
echo -e "${GREEN}🗄️  Checking database...${NC}"
# Add migration check here if needed

# Start the application
echo -e "${GREEN}🌟 Starting application...${NC}"

if [ "$ENVIRONMENT" = "production" ]; then
    echo -e "${GREEN}🏭 Starting in production mode with Gunicorn...${NC}"
    cd src
    exec gunicorn main:app -c ../gunicorn.conf.py
else
    echo -e "${GREEN}🛠️  Starting in development mode...${NC}"
    cd src
    exec python main.py
fi