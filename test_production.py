#!/usr/bin/env python3
"""
Production readiness test for EduTech Platform API
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
backend_dir = Path(__file__).parent / "backend"
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

# Change to backend directory for .env loading
os.chdir(backend_dir)

async def test_production_setup():
    """Test production setup components"""
    print("🧪 Testing EduTech Platform Production Setup")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Import main application
    total_tests += 1
    try:
        from main import app
        print("✅ 1. Application imports successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ 1. Application import failed: {str(e)}")
    
    # Test 2: Test configuration loading
    total_tests += 1
    try:
        from core.config import settings
        print(f"✅ 2. Configuration loaded (Environment: {settings.ENVIRONMENT})")
        tests_passed += 1
    except Exception as e:
        print(f"❌ 2. Configuration loading failed: {str(e)}")
    
    # Test 3: Test database utilities
    total_tests += 1
    try:
        from utils.database import init_database, async_session_factory
        init_database()
        print("✅ 3. Database initialization successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ 3. Database initialization failed: {str(e)}")
    
    # Test 4: Test Telegram bot service
    total_tests += 1
    try:
        from services.telegram_bot import TelegramBotService
        bot = TelegramBotService()
        print("✅ 4. Telegram bot service created")
        tests_passed += 1
    except Exception as e:
        print(f"❌ 4. Telegram bot service failed: {str(e)}")
    
    # Test 5: Test API routes
    total_tests += 1
    try:
        from api.telegram import router
        print("✅ 5. API routes loaded successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ 5. API routes loading failed: {str(e)}")
    
    # Test 6: Test middleware
    total_tests += 1
    try:
        from middleware.error_handler import global_exception_handler
        print("✅ 6. Error handling middleware loaded")
        tests_passed += 1
    except Exception as e:
        print(f"❌ 6. Middleware loading failed: {str(e)}")
    
    # Test 7: Test models
    total_tests += 1
    try:
        from models.user import User
        from models.telegram import TelegramUser
        print("✅ 7. Database models loaded")
        tests_passed += 1
    except Exception as e:
        print(f"❌ 7. Models loading failed: {str(e)}")
    
    # Test 8: Test database connection
    total_tests += 1
    try:
        from utils.database import async_session_factory
        from sqlalchemy import text
        if async_session_factory:
            async with async_session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                result.scalar()
            print("✅ 8. Database connection successful")
            tests_passed += 1
        else:
            print("❌ 8. Database session factory not initialized")
    except Exception as e:
        print(f"❌ 8. Database connection failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Production setup is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_production_setup())
    sys.exit(0 if success else 1)