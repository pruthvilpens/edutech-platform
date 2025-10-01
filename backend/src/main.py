from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys
import asyncio
from contextlib import asynccontextmanager

from core.config import settings
from api.telegram import router as telegram_router
from api.whatsapp import router as whatsapp_router
from api.documents import router as documents_router
from services.telegram_bot import telegram_bot
from utils.database import init_database, close_database
from middleware.error_handler import global_exception_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info("Application starting up...")
    
    # Initialize database
    init_database()
    
    # Initialize Telegram bot
    try:
        await telegram_bot.initialize()
        
        # Start bot in polling mode for development
        if settings.DEBUG and not settings.TELEGRAM_WEBHOOK_URL:
            asyncio.create_task(telegram_bot.start_polling())
            logger.info("Telegram bot started in polling mode")
        elif settings.TELEGRAM_WEBHOOK_URL:
            await telegram_bot.start_webhook()
            logger.info("Telegram bot webhook configured")
            
        logger.info("Application startup completed")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")
    try:
        await telegram_bot.stop()
        await close_database()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO" if not settings.DEBUG else "DEBUG",
)

# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Security Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["yourdomain.com"],
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add global exception handler
app.add_exception_handler(Exception, global_exception_handler)

# Include routers
app.include_router(telegram_router, prefix="/api")
app.include_router(whatsapp_router, prefix="/api")
app.include_router(documents_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }
    )

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with service status"""
    from utils.database import async_session_factory
    
    health_status = {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {}
    }
    
    # Check database connection
    try:
        if async_session_factory:
            async with async_session_factory() as session:
                await session.execute("SELECT 1")
            health_status["services"]["database"] = "healthy"
        else:
            health_status["services"]["database"] = "not_initialized"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Telegram bot status
    try:
        if telegram_bot.application:
            health_status["services"]["telegram_bot"] = "healthy"
        else:
            health_status["services"]["telegram_bot"] = "not_initialized"
    except Exception as e:
        health_status["services"]["telegram_bot"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "YeeBitz Platform API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs" if settings.DEBUG else "Documentation disabled in production",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )