#!/usr/bin/env python3
"""
Simple test to verify Telegram bot can connect
"""
import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_bot():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return False
    
    try:
        bot = Bot(token=token)
        me = await bot.get_me()
        print(f"✅ Bot connected successfully!")
        print(f"   Bot name: {me.first_name}")
        print(f"   Bot username: @{me.username}")
        print(f"   Bot ID: {me.id}")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to bot: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_bot())
    exit(0 if success else 1)