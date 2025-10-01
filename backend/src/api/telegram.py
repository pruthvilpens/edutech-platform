from fastapi import APIRouter, HTTPException, Depends, Request, Header
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from datetime import datetime
from loguru import logger

from core.config import settings
from models.telegram import TelegramUser
from models.user import User
from schemas.telegram import TelegramLinkRequest, TelegramLinkResponse, TelegramWebhookData
from services.telegram_bot import telegram_bot
from utils.database import get_db_session
from utils.auth import get_current_user

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db_session)
):
    """Handle Telegram webhook updates"""
    
    # Verify webhook secret if configured
    if settings.TELEGRAM_WEBHOOK_SECRET:
        if x_telegram_bot_api_secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
            logger.warning("Invalid webhook secret token")
            raise HTTPException(status_code=403, detail="Invalid secret token")
    
    try:
        update_data = await request.json()
        await telegram_bot.process_webhook_update(update_data)
        return JSONResponse({"status": "ok"})
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/link")
async def telegram_link_page(
    token: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Telegram link page - returns link status and instructions"""
    
    # Find telegram user by link token
    result = await db.execute(
        select(TelegramUser).where(
            TelegramUser.link_token == token,
            TelegramUser.link_token_expires_at > datetime.utcnow()
        )
    )
    telegram_user = result.scalar_one_or_none()
    
    if not telegram_user:
        raise HTTPException(
            status_code=404, 
            detail="Invalid or expired link token"
        )
    
    return {
        "telegram_id": telegram_user.telegram_id,
        "telegram_username": telegram_user.telegram_username,
        "telegram_first_name": telegram_user.telegram_first_name,
        "is_linked": telegram_user.is_linked,
        "token": token
    }


@router.post("/link")
async def link_telegram_account(
    link_request: TelegramLinkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Link user's YeeBitz account with Telegram"""
    
    # Find telegram user by link token
    result = await db.execute(
        select(TelegramUser).where(
            TelegramUser.link_token == link_request.token,
            TelegramUser.link_token_expires_at > datetime.utcnow()
        )
    )
    telegram_user = result.scalar_one_or_none()
    
    if not telegram_user:
        raise HTTPException(
            status_code=404,
            detail="Invalid or expired link token"
        )
    
    if telegram_user.is_linked:
        raise HTTPException(
            status_code=400,
            detail="This Telegram account is already linked"
        )
    
    # Check if user already has a linked Telegram account
    existing_link = await db.execute(
        select(TelegramUser).where(
            TelegramUser.user_id == current_user.id,
            TelegramUser.is_linked == True
        )
    )
    if existing_link.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Your account is already linked to another Telegram account"
        )
    
    # Link the accounts
    await db.execute(
        update(TelegramUser)
        .where(TelegramUser.id == telegram_user.id)
        .values(
            user_id=current_user.id,
            is_linked=True,
            linked_at=datetime.utcnow(),
            link_token=None,
            link_token_expires_at=None
        )
    )
    
    # REMOVED: This block is no longer needed
    
    await db.commit()
    
    logger.info(f"Successfully linked user {current_user.email} with Telegram {telegram_user.telegram_id}")
    
    return TelegramLinkResponse(
        success=True,
        message="Successfully linked your accounts!",
        telegram_username=telegram_user.telegram_username,
        user_name=current_user.full_name
    )


@router.delete("/unlink")
async def unlink_telegram_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Unlink user's Telegram account"""
    
    # Find linked telegram account
    result = await db.execute(
        select(TelegramUser).where(
            TelegramUser.user_id == current_user.id,
            TelegramUser.is_linked == True
        )
    )
    telegram_user = result.scalar_one_or_none()
    
    if not telegram_user:
        raise HTTPException(
            status_code=404,
            detail="No linked Telegram account found"
        )
    
    # Unlink accounts
    await db.execute(
        update(TelegramUser)
        .where(TelegramUser.id == telegram_user.id)
        .values(
            user_id=None,
            is_linked=False,
            linked_at=None
        )
    )
    
    # REMOVED: This block is no longer needed
    
    await db.commit()
    
    logger.info(f"Successfully unlinked user {current_user.email} from Telegram {telegram_user.telegram_id}")
    
    return {"success": True, "message": "Successfully unlinked Telegram account"}


@router.get("/status")
async def get_telegram_link_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current user's Telegram link status"""
    
    result = await db.execute(
        select(TelegramUser).where(
            TelegramUser.user_id == current_user.id,
            TelegramUser.is_linked == True
        )
    )
    telegram_user = result.scalar_one_or_none()
    
    if telegram_user:
        return {
            "is_linked": True,
            "telegram_username": telegram_user.telegram_username,
            "telegram_first_name": telegram_user.telegram_first_name,
            "linked_at": telegram_user.linked_at
        }
    else:
        return {
            "is_linked": False,
            "telegram_username": None,
            "telegram_first_name": None,
            "linked_at": None
        }