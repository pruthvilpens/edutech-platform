import asyncio
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Callable

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from loguru import logger
from sqlalchemy import select
from sqlalchemy import update as sqlalchemy_update  # Import with an alias
from sqlalchemy.ext.asyncio import AsyncSession  # <-- FIX 1: Add this import
from core.config import settings


class TelegramBotService:
    def __init__(self):
        self.application = None
        self.db_session_factory = None
        
    async def initialize(self):
        """Initialize the Telegram bot application"""
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.warning("TELEGRAM_BOT_TOKEN not configured, Telegram bot disabled")
            return
        
        # Ensure database is initialized and get the factory
        from utils.database import init_database, async_session_factory
        init_database()
        
        # Store session factory
        self.db_session_factory = async_session_factory
        
        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("link", self.link_command))
        self.application.add_handler(CommandHandler("unlink", self.unlink_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("Telegram bot initialized successfully")
        
    async def start_webhook(self):
        """Start webhook mode"""
        if not self.application or not settings.TELEGRAM_WEBHOOK_URL:
            return
            
        await self.application.initialize()
        await self.application.start()
        await self.application.bot.set_webhook(
            url=settings.TELEGRAM_WEBHOOK_URL,
            secret_token=settings.TELEGRAM_WEBHOOK_SECRET
        )
        logger.info(f"Webhook set to: {settings.TELEGRAM_WEBHOOK_URL}")
        
    async def start_polling(self):
        """Start polling mode for development"""
        if not self.application:
            return
            
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("Bot started in polling mode")
        
    async def stop(self):
        """Stop the bot"""
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
            
    async def process_webhook_update(self, update_data: dict):
        """Process webhook update"""
        if not self.application:
            return
            
        update = Update.de_json(update_data, self.application.bot)
        await self.application.process_update(update)
        
    def generate_link_token(self) -> str:
        """Generate a secure link token"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        
    async def get_or_create_telegram_user(self, session: AsyncSession, telegram_id: int, user_data: dict):
        """Get or create telegram user record"""
        # Import here to avoid circular imports
        from models.telegram import TelegramUser
        
        # Check if telegram user exists
        result = await session.execute(
            select(TelegramUser).where(TelegramUser.telegram_id == telegram_id)
        )
        telegram_user = result.scalar_one_or_none()
        
        if not telegram_user:
            # Create new telegram user
            telegram_user = TelegramUser(
                telegram_id=telegram_id,
                telegram_username=user_data.get('username'),
                telegram_first_name=user_data.get('first_name'),
                telegram_last_name=user_data.get('last_name')
            )
            session.add(telegram_user)
            await session.commit()
            await session.refresh(telegram_user)
            
        return telegram_user
            
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        async with self.db_session_factory() as session:
            telegram_user = await self.get_or_create_telegram_user(
                session,
                user.id, 
                {
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            )
            
            welcome_message = (
                f"🎓 Welcome to YeetBitz  Bot!\n\n"
                f"Hi {user.first_name}! I can help you take tests and access your study materials.\n\n"
                f"Available commands:\n"
                f"• /link - Link your account\n"
                f"• /status - Check linking status\n"
                f"• /unlink - Unlink your account\n\n"
                f"To get started, please link your YeeBitz account using /link"
            )
            
            keyboard = [
                [InlineKeyboardButton("🔗 Link Account", callback_data="link_account")],
                [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        
    async def link_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /link command"""
        from models.telegram import TelegramUser
        
        user = update.effective_user
        
        async with self.db_session_factory() as session:
            # Check if already linked
            result = await session.execute(
                select(TelegramUser).where(
                    TelegramUser.telegram_id == user.id,
                    TelegramUser.is_linked == True
                )
            )
            telegram_user = result.scalar_one_or_none()
            
            if telegram_user:
                await update.message.reply_text(
                    "✅ Your account is already linked!\n"
                    "Use /status to view details or /unlink to disconnect."
                )
                return
                
            # Get or create telegram user
            telegram_user = await self.get_or_create_telegram_user(
                session,
                user.id,
                {
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            )
            
            # Generate link token
            link_token = self.generate_link_token()
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            await session.execute(
                sqlalchemy_update(TelegramUser)
                .where(TelegramUser.telegram_id == user.id)
                .values(
                    link_token=link_token,
                    link_token_expires_at=expires_at
                )
            )
            await session.commit()
                
            link_url = f"{settings.CORS_ORIGINS[0]}/telegram/link?token={link_token}"
            
            # --- MODIFICATION START ---
            
            message = (
                f"🔗 Account Linking\n\n"
                f"To link your YeeBitz account, copy the link below and open it in your browser:\n\n"
                f"➡️ {link_url}\n\n"
                f"Alternatively, go to the settings page and paste this token:\n"
                f"`{link_token}`\n\n"
                f"⏰ This link expires in 1 hour.\n"
                f"🔒 For security, don't share this with others."
            )
            
            # We send the message without any buttons (reply_markup)
            await update.message.reply_text(message, parse_mode='Markdown')
            
    async def unlink_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unlink command"""
        from models.telegram import TelegramUser
        
        user = update.effective_user
        
        async with self.db_session_factory() as session:
            result = await session.execute(
                select(TelegramUser).where(TelegramUser.telegram_id == user.id)
            )
            telegram_user = result.scalar_one_or_none()
            
            if not telegram_user or not telegram_user.is_linked:
                await update.message.reply_text(
                    "❌ No linked account found.\n"
                    "Use /link to connect your YeeBitz account."
                )
                return
                
            # Unlink account
            await session.execute(
                sqlalchemy_update(TelegramUser)  # Use the new alias
                .where(TelegramUser.telegram_id == user.id)
                .values(
                    is_linked=False,
                    user_id=None,
                    linked_at=None,
                    link_token=None,
                    link_token_expires_at=None
                )
            )
            await session.commit()
            
            await update.message.reply_text(
                "✅ Account unlinked successfully!\n"
                "Use /link to connect again anytime."
            )
            
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        from models.telegram import TelegramUser
        from models.user import User
        
        user = update.effective_user
        
        async with self.db_session_factory() as session:
            result = await session.execute(
                select(TelegramUser, User)
                .outerjoin(User, TelegramUser.user_id == User.id)
                .where(TelegramUser.telegram_id == user.id)
            )
            row = result.first()
            
            if not row or not row[0]:
                await update.message.reply_text(
                    "❌ No account record found.\n"
                    "Use /start to initialize and /link to connect."
                )
                return
                
            telegram_user, linked_user = row
            
            if telegram_user.is_linked and linked_user:
                status_message = (
                    f"✅ Account Status: Linked\n\n"
                    f"👤 YeeBitz Account: {linked_user.full_name}\n"
                    f"📧 Email: {linked_user.email}\n"
                    f"🎭 Role: {linked_user.role}\n"
                    f"🔗 Linked: {telegram_user.linked_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"Ready to take tests! 🎓"
                )
            else:
                status_message = (
                    f"❌ Account Status: Not Linked\n\n"
                    f"Use /link to connect your YeeBitz account."
                )
                
            await update.message.reply_text(status_message)
            
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "link_account":
            await self.link_command(update, context)
        elif query.data == "help":
            help_message = (
                "🎓 YeeBitz Platform Bot Help\n\n"
                "This bot allows you to:\n"
                "• Link your YeeBitz account\n"
                "• Take tests directly from Telegram\n"
                "• View your progress and results\n\n"
                "Commands:\n"
                "• /start - Welcome message\n"
                "• /link - Link your account\n"
                "• /status - Check status\n"
                "• /unlink - Disconnect account\n\n"
                "Need more help? Contact support."
            )
            await query.edit_message_text(help_message)
        elif query.data == "regenerate_link":
            await self.link_command(update, context)


# Global bot instance
telegram_bot = TelegramBotService()