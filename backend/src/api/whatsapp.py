from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from datetime import datetime
from loguru import logger

from core.config import settings
from models.whatsapp import WhatsAppUser
from models.user import User
from schemas.whatsapp import (
    WhatsAppLinkRequest, 
    WhatsAppLinkResponse, 
    WhatsAppWebhookData,
    WhatsAppLinkStatusResponse,
    WhatsAppUserResponse,
    WhatsAppSendMessageRequest,
    WhatsAppSendMessageResponse,
    WhatsAppVerificationRequest
)
from utils.database import get_db_session
from utils.auth import get_current_user

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token")
):
    """Verify WhatsApp webhook endpoint"""
    
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully")
        return PlainTextResponse(hub_challenge)
    
    logger.warning(f"Invalid webhook verification attempt: mode={hub_mode}, token={hub_verify_token}")
    raise HTTPException(status_code=403, detail="Invalid verification token")


@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Handle WhatsApp webhook updates"""
    
    try:
        webhook_data = await request.json()
        logger.info(f"Received WhatsApp webhook: {webhook_data}")
        
        # Validate webhook signature if configured
        if settings.WHATSAPP_WEBHOOK_SECRET:
            signature = request.headers.get("x-hub-signature-256")
            if not signature:
                logger.warning("Missing webhook signature")
                raise HTTPException(status_code=403, detail="Missing signature")
            
            # TODO: Implement signature verification
            # This should be implemented by the WhatsApp developer
        
        # Parse webhook data
        try:
            parsed_data = WhatsAppWebhookData(**webhook_data)
        except Exception as e:
            logger.error(f"Failed to parse webhook data: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid webhook data format")
        
        # Process webhook entries
        for entry in parsed_data.entry:
            for change in entry.changes:
                if change.get("field") == "messages":
                    value = change.get("value", {})
                    
                    # Process incoming messages
                    messages = value.get("messages", [])
                    for message in messages:
                        await process_whatsapp_message(message, db)
                    
                    # Process message statuses
                    statuses = value.get("statuses", [])
                    for status in statuses:
                        await process_whatsapp_status(status, db)
        
        return JSONResponse({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_whatsapp_message(message: dict, db: AsyncSession):
    """Process incoming WhatsApp message"""
    
    phone_number = message.get("from")
    message_type = message.get("type")
    message_id = message.get("id")
    
    logger.info(f"Processing message {message_id} from {phone_number} of type {message_type}")
    
    # Get or create WhatsApp user
    result = await db.execute(
        select(WhatsAppUser).where(WhatsAppUser.whatsapp_phone == phone_number)
    )
    whatsapp_user = result.scalar_one_or_none()
    
    if not whatsapp_user:
        # Create new WhatsApp user
        whatsapp_user = WhatsAppUser(
            whatsapp_phone=phone_number,
            whatsapp_name=message.get("profile", {}).get("name")
        )
        db.add(whatsapp_user)
        await db.commit()
        await db.refresh(whatsapp_user)
    
    # Process different message types
    if message_type == "text":
        text_content = message.get("text", {}).get("body", "").strip().lower()
        
        if text_content in ["/start", "start", "hi", "hello"]:
            await send_welcome_message(phone_number)
        elif text_content in ["/link", "link"]:
            await handle_link_command(whatsapp_user, db)
        elif text_content in ["/status", "status"]:
            await handle_status_command(whatsapp_user, db)
        elif text_content in ["/unlink", "unlink"]:
            await handle_unlink_command(whatsapp_user, db)
        else:
            await send_help_message(phone_number)


async def process_whatsapp_status(status: dict, db: AsyncSession):
    """Process WhatsApp message status update"""
    
    message_id = status.get("id")
    status_type = status.get("status")
    
    logger.info(f"Message {message_id} status: {status_type}")
    
    # TODO: Implement status tracking if needed
    # This can be used for delivery confirmations, read receipts, etc.


async def send_welcome_message(phone_number: str):
    """Send welcome message to WhatsApp user"""
    
    message = (
        "🎓 Welcome to YeetBitz Platform!\n\n"
        "I can help you take tests and access your study materials.\n\n"
        "Available commands:\n"
        "• Send 'link' - Link your account\n"
        "• Send 'status' - Check linking status\n" 
        "• Send 'unlink' - Unlink your account\n\n"
        "To get started, please link your YeeBitz account by sending 'link'"
    )
    
    await send_whatsapp_message(phone_number, message)


async def handle_link_command(whatsapp_user: WhatsAppUser, db: AsyncSession):
    """Handle link command from WhatsApp"""
    
    if whatsapp_user.is_linked:
        message = (
            "✅ Your account is already linked!\n"
            "Send 'status' to view details or 'unlink' to disconnect."
        )
        await send_whatsapp_message(whatsapp_user.whatsapp_phone, message)
        return
    
    # Generate link token (implement this similar to Telegram)
    import secrets
    import string
    from datetime import timedelta
    
    link_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    await db.execute(
        update(WhatsAppUser)
        .where(WhatsAppUser.id == whatsapp_user.id)
        .values(
            link_token=link_token,
            link_token_expires_at=expires_at
        )
    )
    await db.commit()
    
    link_url = f"{settings.CORS_ORIGINS[0]}/whatsapp/link?token={link_token}"
    
    message = (
        f"🔗 Account Linking\n\n"
        f"To link your YeeBitz account, open this link in your browser:\n\n"
        f"👉 {link_url}\n\n"
        f"Or go to the settings page and paste this token:\n"
        f"{link_token}\n\n"
        f"⏰ This link expires in 1 hour.\n"
        f"🔒 For security, don't share this with others."
    )
    
    await send_whatsapp_message(whatsapp_user.whatsapp_phone, message)


async def handle_status_command(whatsapp_user: WhatsAppUser, db: AsyncSession):
    """Handle status command from WhatsApp"""
    
    if whatsapp_user.is_linked:
        # Get linked user details
        result = await db.execute(
            select(User).where(User.id == whatsapp_user.user_id)
        )
        linked_user = result.scalar_one_or_none()
        
        if linked_user:
            message = (
                f"✅ Account Status: Linked\n\n"
                f"👤 YeeBitz Account: {linked_user.full_name}\n"
                f"📧 Email: {linked_user.email}\n"
                f"🎭 Role: {linked_user.role}\n"
                f"🔗 Linked: {whatsapp_user.linked_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                f"Ready to take tests! 🎓"
            )
        else:
            message = "❌ Error: Linked user not found. Please contact support."
    else:
        message = (
            f"❌ Account Status: Not Linked\n\n"
            f"Send 'link' to connect your YeeBitz account."
        )
    
    await send_whatsapp_message(whatsapp_user.whatsapp_phone, message)


async def handle_unlink_command(whatsapp_user: WhatsAppUser, db: AsyncSession):
    """Handle unlink command from WhatsApp"""
    
    if not whatsapp_user.is_linked:
        message = (
            "❌ No linked account found.\n"
            "Send 'link' to connect your YeeBitz account."
        )
        await send_whatsapp_message(whatsapp_user.whatsapp_phone, message)
        return
    
    # Unlink account
    await db.execute(
        update(WhatsAppUser)
        .where(WhatsAppUser.id == whatsapp_user.id)
        .values(
            is_linked=False,
            user_id=None,
            linked_at=None,
            link_token=None,
            link_token_expires_at=None
        )
    )
    await db.commit()
    
    message = (
        "✅ Account unlinked successfully!\n"
        "Send 'link' to connect again anytime."
    )
    
    await send_whatsapp_message(whatsapp_user.whatsapp_phone, message)


async def send_help_message(phone_number: str):
    """Send help message to WhatsApp user"""
    
    message = (
        "🎓 YeeBitz Platform Bot Help\n\n"
        "Available commands:\n"
        "• Send 'start' - Welcome message\n"
        "• Send 'link' - Link your account\n"
        "• Send 'status' - Check status\n"
        "• Send 'unlink' - Disconnect account\n\n"
        "Need more help? Contact support."
    )
    
    await send_whatsapp_message(phone_number, message)


async def send_whatsapp_message(phone_number: str, message: str):
    """Send WhatsApp message via API"""
    
    # TODO: Implement actual WhatsApp API call
    # This should be implemented by the WhatsApp developer using their preferred method
    logger.info(f"Sending WhatsApp message to {phone_number}: {message}")


@router.get("/link")
async def whatsapp_link_page(
    token: str,
    db: AsyncSession = Depends(get_db_session)
):
    """WhatsApp link page - returns link status and instructions"""
    
    # Find WhatsApp user by link token
    result = await db.execute(
        select(WhatsAppUser).where(
            WhatsAppUser.link_token == token,
            WhatsAppUser.link_token_expires_at > datetime.utcnow()
        )
    )
    whatsapp_user = result.scalar_one_or_none()
    
    if not whatsapp_user:
        raise HTTPException(
            status_code=404, 
            detail="Invalid or expired link token"
        )
    
    return {
        "whatsapp_phone": whatsapp_user.whatsapp_phone,
        "whatsapp_name": whatsapp_user.whatsapp_name,
        "is_linked": whatsapp_user.is_linked,
        "token": token
    }


@router.post("/link")
async def link_whatsapp_account(
    link_request: WhatsAppLinkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Link user's YeeBitz account with WhatsApp"""
    
    # Find WhatsApp user by link token
    result = await db.execute(
        select(WhatsAppUser).where(
            WhatsAppUser.link_token == link_request.token,
            WhatsAppUser.link_token_expires_at > datetime.utcnow()
        )
    )
    whatsapp_user = result.scalar_one_or_none()
    
    if not whatsapp_user:
        raise HTTPException(
            status_code=404,
            detail="Invalid or expired link token"
        )
    
    if whatsapp_user.is_linked:
        raise HTTPException(
            status_code=400,
            detail="This WhatsApp account is already linked"
        )
    
    # Check if user already has a linked WhatsApp account
    existing_link = await db.execute(
        select(WhatsAppUser).where(
            WhatsAppUser.user_id == current_user.id,
            WhatsAppUser.is_linked == True
        )
    )
    if existing_link.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Your account is already linked to another WhatsApp account"
        )
    
    # Link the accounts
    await db.execute(
        update(WhatsAppUser)
        .where(WhatsAppUser.id == whatsapp_user.id)
        .values(
            user_id=current_user.id,
            is_linked=True,
            linked_at=datetime.utcnow(),
            link_token=None,
            link_token_expires_at=None
        )
    )
    
    await db.commit()
    
    logger.info(f"Successfully linked user {current_user.email} with WhatsApp {whatsapp_user.whatsapp_phone}")
    
    # Send confirmation message
    await send_whatsapp_message(
        whatsapp_user.whatsapp_phone,
        f"✅ Account linked successfully!\n\nYour YeeBitz account ({current_user.full_name}) is now connected to WhatsApp.\n\nYou can now take tests and access materials directly from WhatsApp! 🎓"
    )
    
    return WhatsAppLinkResponse(
        success=True,
        message="Successfully linked your accounts!",
        whatsapp_phone=whatsapp_user.whatsapp_phone,
        whatsapp_name=whatsapp_user.whatsapp_name,
        user_name=current_user.full_name
    )


@router.delete("/unlink")
async def unlink_whatsapp_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Unlink user's WhatsApp account"""
    
    # Find linked WhatsApp account
    result = await db.execute(
        select(WhatsAppUser).where(
            WhatsAppUser.user_id == current_user.id,
            WhatsAppUser.is_linked == True
        )
    )
    whatsapp_user = result.scalar_one_or_none()
    
    if not whatsapp_user:
        raise HTTPException(
            status_code=404,
            detail="No linked WhatsApp account found"
        )
    
    # Unlink accounts
    await db.execute(
        update(WhatsAppUser)
        .where(WhatsAppUser.id == whatsapp_user.id)
        .values(
            user_id=None,
            is_linked=False,
            linked_at=None
        )
    )
    
    await db.commit()
    
    logger.info(f"Successfully unlinked user {current_user.email} from WhatsApp {whatsapp_user.whatsapp_phone}")
    
    # Send confirmation message
    await send_whatsapp_message(
        whatsapp_user.whatsapp_phone,
        "✅ Account unlinked successfully!\n\nYour YeeBitz account has been disconnected from WhatsApp.\n\nSend 'link' to connect again anytime."
    )
    
    return {"success": True, "message": "Successfully unlinked WhatsApp account"}


@router.get("/status")
async def get_whatsapp_link_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current user's WhatsApp link status"""
    
    result = await db.execute(
        select(WhatsAppUser).where(
            WhatsAppUser.user_id == current_user.id,
            WhatsAppUser.is_linked == True
        )
    )
    whatsapp_user = result.scalar_one_or_none()
    
    if whatsapp_user:
        return WhatsAppLinkStatusResponse(
            is_linked=True,
            whatsapp_phone=whatsapp_user.whatsapp_phone,
            whatsapp_name=whatsapp_user.whatsapp_name,
            linked_at=whatsapp_user.linked_at
        )
    else:
        return WhatsAppLinkStatusResponse(
            is_linked=False,
            whatsapp_phone=None,
            whatsapp_name=None,
            linked_at=None
        )


@router.post("/send")
async def send_message(
    message_request: WhatsAppSendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Send WhatsApp message (admin/instructor only)"""
    
    if current_user.role not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and instructors can send messages"
        )
    
    try:
        # TODO: Implement actual message sending via WhatsApp API
        # This should be implemented by the WhatsApp developer
        
        logger.info(f"Sending WhatsApp message to {message_request.to}: {message_request.text}")
        
        return WhatsAppSendMessageResponse(
            success=True,
            message_id="mock_message_id",
            error=None
        )
        
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {str(e)}")
        return WhatsAppSendMessageResponse(
            success=False,
            message_id=None,
            error=str(e)
        )