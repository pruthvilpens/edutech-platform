#!/usr/bin/env python3
"""
Test Telegram bot with comprehensive logging
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
backend_dir = Path(__file__).parent / "backend"
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

# Change to backend directory for .env loading
import os
os.chdir(backend_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)

# Set specific log levels
logging.getLogger('telegram').setLevel(logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)  # Reduce HTTP noise

async def main():
    """Start bot with logging"""
    print("🤖 Starting EduTech Telegram Bot with Logging")
    print("=" * 50)
    
    try:
        # Import and initialize
        from main import app
        from services.telegram_bot import telegram_bot
        from utils.database import init_database, async_session_factory
        
        # Initialize database
        init_database()
        
        # Initialize bot
        await telegram_bot.initialize(async_session_factory)
        
        if not telegram_bot.application:
            print("❌ Bot failed to initialize")
            return
            
        print("✅ Bot initialized successfully")
        print(f"📱 Bot username: @yeebitz_bot")
        print(f"📝 Logs saved to: {backend_dir}/bot.log")
        print("\n🔍 Live Bot Activity:")
        print("-" * 30)
        
        # Start polling
        await telegram_bot.start_polling()
        
    except KeyboardInterrupt:
        print("\n⏹️  Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logging.error(f"Bot error: {str(e)}", exc_info=True)
    finally:
        if 'telegram_bot' in locals():
            await telegram_bot.stop()

if __name__ == "__main__":
    asyncio.run(main())