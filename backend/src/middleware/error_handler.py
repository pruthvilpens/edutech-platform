from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
import traceback
from typing import Union


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for the application"""
    
    # Log the error
    logger.error(f"Global exception handler caught: {type(exc).__name__}: {str(exc)}")
    logger.error(f"Request URL: {request.url}")
    logger.error(f"Request method: {request.method}")
    
    # Log full traceback in debug mode
    if hasattr(request.app.state, 'settings') and request.app.state.settings.DEBUG:
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Handle specific exception types
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "type": "http_exception"}
        )
    
    # Handle database connection errors
    if "connection" in str(exc).lower() or "database" in str(exc).lower():
        logger.error("Database connection error detected")
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service temporarily unavailable. Please try again later.",
                "type": "database_error"
            }
        )
    
    # Handle Telegram API errors
    if "telegram" in str(exc).lower() or "bot" in str(exc).lower():
        logger.error("Telegram API error detected")
        return JSONResponse(
            status_code=502,
            content={
                "error": "Telegram service temporarily unavailable.",
                "type": "telegram_error"
            }
        )
    
    # Generic server error
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error. Please contact support if the problem persists.",
            "type": "internal_error"
        }
    )