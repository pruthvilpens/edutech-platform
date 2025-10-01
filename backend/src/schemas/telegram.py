from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class TelegramLinkRequest(BaseModel):
    token: str


class TelegramLinkResponse(BaseModel):
    success: bool
    message: str
    telegram_username: Optional[str] = None
    user_name: Optional[str] = None


class TelegramWebhookData(BaseModel):
    update_id: int
    message: Optional[Dict[str, Any]] = None
    callback_query: Optional[Dict[str, Any]] = None


class TelegramUserCreate(BaseModel):
    telegram_id: int
    telegram_username: Optional[str] = None
    telegram_first_name: Optional[str] = None
    telegram_last_name: Optional[str] = None


class TelegramUserResponse(BaseModel):
    id: str
    telegram_id: int
    telegram_username: Optional[str]
    telegram_first_name: Optional[str]
    telegram_last_name: Optional[str]
    is_linked: bool
    linked_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TelegramLinkStatusResponse(BaseModel):
    is_linked: bool
    telegram_username: Optional[str]
    telegram_first_name: Optional[str]
    linked_at: Optional[datetime]