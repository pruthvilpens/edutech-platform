import asyncio
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Callable

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from loguru import logger
from sqlalchemy import select
from sqlalchemy import update as sqlalchemy_update  # Import with an alias
from sqlalchemy.ext.asyncio import AsyncSession  # <-- FIX 1: Add this import
from core.config import settings

# In-memory store for user chat sessions
user_chat_contexts = {}


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
        self.application.add_handler(CommandHandler("documents", self.documents_command))
        self.application.add_handler(CommandHandler("chat", self.chat_command))
        self.application.add_handler(CommandHandler("questions", self.questions_command))
        self.application.add_handler(CommandHandler("summary", self.summary_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
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
                f"🎓 Welcome to YeetBitz Bot!\n\n"
                f"Hi {user.first_name}! I can help you study with your documents and take tests.\n\n"
                f"Available commands:\n"
                f"• /link - Link your account\n"
                f"• /status - Check linking status\n"
                f"• /documents - View available documents\n"
                f"• /chat - Chat with a document\n"
                f"• /questions - Get study questions\n"
                f"• /summary - Get document summary\n"
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

    async def _check_user_linked(self, telegram_id: int) -> Optional[dict]:
        """Check if user is linked and return user data"""
        from models.telegram import TelegramUser
        from models.user import User
        
        async with self.db_session_factory() as session:
            result = await session.execute(
                select(TelegramUser, User)
                .outerjoin(User, TelegramUser.user_id == User.id)
                .where(TelegramUser.telegram_id == telegram_id)
            )
            row = result.first()
            
            if not row or not row[0] or not row[0].is_linked or not row[1]:
                return None
                
            telegram_user, linked_user = row
            return {
                "telegram_user": telegram_user,
                "user": linked_user
            }

    async def documents_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /documents command"""
        user = update.effective_user
        
        # Check if user is linked
        user_data = await self._check_user_linked(user.id)
        if not user_data:
            await update.message.reply_text(
                "❌ Please link your account first using /link to access documents."
            )
            return
            
        # Get user's accessible documents
        from models.document import Document, DocumentStatus
        from models.user import UserRole
        
        async with self.db_session_factory() as session:
            current_user = user_data["user"]
            
            # Build query based on user role
            query = select(Document).where(Document.status == DocumentStatus.processed)
            
            if current_user.role == UserRole.INSTRUCTOR.value:
                # Instructors can see their own documents and all processed ones
                from sqlalchemy import or_
                query = query.where(
                    or_(
                        Document.uploaded_by == current_user.id,
                        Document.status == DocumentStatus.processed
                    )
                )
            # Students can only see processed documents (already filtered above)
            
            result = await session.execute(query.order_by(Document.created_at.desc()).limit(10))
            documents = result.scalars().all()
            
            if not documents:
                await update.message.reply_text(
                    "📚 No documents available at the moment.\n"
                    "Contact your instructor to upload study materials."
                )
                return
            
            # Create inline keyboard with documents
            keyboard = []
            for doc in documents:
                keyboard.append([
                    InlineKeyboardButton(
                        f"📄 {doc.original_filename[:30]}...", 
                        callback_data=f"doc_{doc.id}"
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📚 Available Documents:\n\nSelect a document to interact with:",
                reply_markup=reply_markup
            )

    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chat command"""
        user = update.effective_user
        
        # Check if user is linked
        user_data = await self._check_user_linked(user.id)
        if not user_data:
            await update.message.reply_text(
                "❌ Please link your account first using /link to chat with documents."
            )
            return
            
        # Parse command arguments
        if context.args:
            await update.message.reply_text(
                "💬 To chat with a document:\n"
                "1. Use /documents to see available documents\n"
                "2. Select a document and choose 'Chat'\n"
                "3. Then type your questions normally"
            )
        else:
            await update.message.reply_text(
                "💬 Document Chat\n\n"
                "First, select a document using /documents, then you can chat with it!\n"
                "Or use /documents to see available documents."
            )

    async def questions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /questions command"""
        user = update.effective_user
        
        # Check if user is linked
        user_data = await self._check_user_linked(user.id)
        if not user_data:
            await update.message.reply_text(
                "❌ Please link your account first using /link to get study questions."
            )
            return
            
        await update.message.reply_text(
            "❓ Study Questions\n\n"
            "To get study questions for a document:\n"
            "1. Use /documents to see available documents\n"
            "2. Select a document and choose 'Study Questions'\n\n"
            "Or use /documents to browse available documents."
        )

    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /summary command"""
        user = update.effective_user
        
        # Check if user is linked
        user_data = await self._check_user_linked(user.id)
        if not user_data:
            await update.message.reply_text(
                "❌ Please link your account first using /link to get document summaries."
            )
            return
            
        await update.message.reply_text(
            "📝 Document Summary\n\n"
            "To get a summary of a document:\n"
            "1. Use /documents to see available documents\n"
            "2. Select a document and choose 'Summary'\n\n"
            "Or use /documents to browse available documents."
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages for document chat"""
        user = update.effective_user
        message_text = update.message.text
        
        # Check if user is linked
        user_data = await self._check_user_linked(user.id)
        if not user_data:
            await update.message.reply_text(
                "❌ Please link your account first using /link to chat with documents."
            )
            return
        
        # Check if user has an active chat session
        if user.id not in user_chat_contexts:
            await update.message.reply_text(
                "💬 No active document chat session.\n\n"
                "To start chatting with a document:\n"
                "1. Use /documents to see available documents\n"
                "2. Select a document and choose 'Chat'"
            )
            return
        
        # Get active document ID
        document_id = user_chat_contexts[user.id]
        
        # Process the chat message
        await self._process_chat_message(update, document_id, message_text, user_data["user"])

    async def _show_document_options(self, query, document_id: str):
        """Show options for a selected document"""
        keyboard = [
            [InlineKeyboardButton("💬 Chat", callback_data=f"chat_{document_id}")],
            [InlineKeyboardButton("❓ Study Questions", callback_data=f"questions_{document_id}")],
            [InlineKeyboardButton("📝 Summary", callback_data=f"summary_{document_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📄 Document Options:\n\nWhat would you like to do with this document?",
            reply_markup=reply_markup
        )

    async def _start_document_chat(self, query, document_id: str):
        """Start chat session with a document"""
        user_id = query.from_user.id
        
        # Set user's active chat context
        user_chat_contexts[user_id] = document_id
        
        await query.edit_message_text(
            "💬 Chat session started!\n\n"
            "You can now type your questions about this document.\n"
            "I'll answer based on the document content.\n\n"
            "Type any question to get started!"
        )

    async def _process_chat_message(self, update: Update, document_id: str, message: str, user):
        """Process a chat message with the document"""
        try:
            from models.document import Document, DocumentChatSession, ChatMessage
            from services.gemini_service import gemini_service
            from sqlalchemy import and_
            
            async with self.db_session_factory() as session:
                # Get document
                doc_result = await session.execute(
                    select(Document).where(Document.id == document_id)
                )
                document = doc_result.scalar_one_or_none()
                
                if not document:
                    await update.message.reply_text("❌ Document not found.")
                    return
                
                # Get or create chat session
                session_result = await session.execute(
                    select(DocumentChatSession).where(
                        and_(
                            DocumentChatSession.document_id == document_id,
                            DocumentChatSession.user_id == user.id
                        )
                    )
                )
                chat_session = session_result.scalar_one_or_none()
                
                if not chat_session:
                    chat_session = DocumentChatSession(
                        document_id=document_id,
                        user_id=user.id,
                        session_name=f"Telegram Chat with {document.original_filename}"
                    )
                    session.add(chat_session)
                    await session.commit()
                    await session.refresh(chat_session)
                
                # Save user message
                user_message = ChatMessage(
                    session_id=chat_session.id,
                    role="user",
                    content=message
                )
                session.add(user_message)
                await session.commit()
                
                # Get chat history
                history_result = await session.execute(
                    select(ChatMessage)
                    .where(ChatMessage.session_id == chat_session.id)
                    .order_by(ChatMessage.created_at.desc())
                    .limit(20)
                )
                chat_history = [
                    {"role": msg.role, "content": msg.content} 
                    for msg in reversed(history_result.scalars().all()[:-1])
                ]
                
                # Send typing indicator
                await update.message.chat.send_action("typing")
                
                # Get AI response
                ai_response_data = await gemini_service.chat_with_document(
                    document.processed_text,
                    message,
                    chat_history
                )
                
                if ai_response_data["success"]:
                    # Save AI response
                    ai_message = ChatMessage(
                        session_id=chat_session.id,
                        role="assistant",
                        content=ai_response_data["response"],
                        message_metadata={"model_used": ai_response_data.get("model_used", "unknown")}
                    )
                    session.add(ai_message)
                    await session.commit()
                    
                    # Send response to user
                    await update.message.reply_text(ai_response_data["response"])
                else:
                    await update.message.reply_text(
                        "😔 Sorry, I encountered an error while processing your question. Please try again."
                    )
                    
        except Exception as e:
            logger.error(f"Error in chat processing: {str(e)}")
            await update.message.reply_text(
                "😔 An error occurred while processing your message. Please try again."
            )

    async def _get_document_questions(self, query, document_id: str):
        """Get study questions for a document"""
        try:
            from models.document import Document
            from services.gemini_service import gemini_service
            
            async with self.db_session_factory() as session:
                # Get document
                result = await session.execute(
                    select(Document).where(Document.id == document_id)
                )
                document = result.scalar_one_or_none()
                
                if not document:
                    await query.edit_message_text("❌ Document not found.")
                    return
                
                # Check if we have cached questions
                if document.cached_study_questions:
                    await query.edit_message_text(
                        f"❓ Study Questions for {document.original_filename}:\n\n"
                        f"{document.cached_study_questions}"
                    )
                    return
                
                # Generate new questions
                await query.edit_message_text("⏳ Generating study questions...")
                
                questions_data = await gemini_service.suggest_study_questions(document.processed_text)
                
                if questions_data["success"]:
                    # Cache the questions
                    document.cached_study_questions = questions_data["questions"]
                    document.questions_generated_at = datetime.utcnow()
                    await session.commit()
                    
                    await query.edit_message_text(
                        f"❓ Study Questions for {document.original_filename}:\n\n"
                        f"{questions_data['questions']}"
                    )
                else:
                    await query.edit_message_text(
                        "😔 Sorry, I couldn't generate study questions at the moment. Please try again."
                    )
                    
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            await query.edit_message_text(
                "😔 An error occurred while generating questions. Please try again."
            )

    async def _get_document_summary(self, query, document_id: str):
        """Get summary for a document"""
        try:
            from models.document import Document
            from services.gemini_service import gemini_service
            
            async with self.db_session_factory() as session:
                # Get document
                result = await session.execute(
                    select(Document).where(Document.id == document_id)
                )
                document = result.scalar_one_or_none()
                
                if not document:
                    await query.edit_message_text("❌ Document not found.")
                    return
                
                # Check if we have cached summary
                if document.cached_summary:
                    await query.edit_message_text(
                        f"📝 Summary of {document.original_filename}:\n\n"
                        f"{document.cached_summary}"
                    )
                    return
                
                # Generate new summary
                await query.edit_message_text("⏳ Generating summary...")
                
                summary_data = await gemini_service.extract_document_summary(document.processed_text)
                
                if summary_data["success"]:
                    # Cache the summary
                    document.cached_summary = summary_data["summary"]
                    document.summary_generated_at = datetime.utcnow()
                    await session.commit()
                    
                    await query.edit_message_text(
                        f"📝 Summary of {document.original_filename}:\n\n"
                        f"{summary_data['summary']}"
                    )
                else:
                    await query.edit_message_text(
                        "😔 Sorry, I couldn't generate a summary at the moment. Please try again."
                    )
                    
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            await query.edit_message_text(
                "😔 An error occurred while generating summary. Please try again."
            )
            
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
                "• Chat with documents using AI\n"
                "• Get study questions and summaries\n"
                "• Take tests directly from Telegram\n\n"
                "Commands:\n"
                "• /start - Welcome message\n"
                "• /link - Link your account\n"
                "• /status - Check status\n"
                "• /documents - View available documents\n"
                "• /chat - Chat with documents\n"
                "• /questions - Get study questions\n"
                "• /summary - Get document summaries\n"
                "• /unlink - Disconnect account\n\n"
                "Need more help? Contact support."
            )
            await query.edit_message_text(help_message)
        elif query.data == "regenerate_link":
            await self.link_command(update, context)
        elif query.data.startswith("doc_"):
            document_id = query.data[4:]
            await self._show_document_options(query, document_id)
        elif query.data.startswith("chat_"):
            document_id = query.data[5:]
            await self._start_document_chat(query, document_id)
        elif query.data.startswith("questions_"):
            document_id = query.data[10:]
            await self._get_document_questions(query, document_id)
        elif query.data.startswith("summary_"):
            document_id = query.data[8:]
            await self._get_document_summary(query, document_id)


# Global bot instance
telegram_bot = TelegramBotService()