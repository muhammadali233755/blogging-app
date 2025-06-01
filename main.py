import logging
import uuid
from typing import Dict, Any, List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
import time

# Config imports
from config import get_settings

# Database imports
from database import engine, SessionLocal
import model

# Router imports
from router import auth, category, comment, like, post, user

# Utility imports
from utils import user_dependency, db_dependency

# Load settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Environment configuration from settings
ENVIRONMENT = settings.ENVIRONMENT
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS
RATE_LIMIT = settings.RATE_LIMIT
DEBUG = settings.DEBUG

# Security configuration from settings
SECRET_KEY = settings.SECRET_KEY
TRUSTED_HOSTS = settings.TRUSTED_HOSTS
SESSION_COOKIE_NAME = settings.SESSION_COOKIE_NAME

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if ENVIRONMENT == "development":
            return await call_next(request)
            
        # Simple rate limiting by IP
        client_ip = request.client.host
        current_time = time.time()
        request_count = request.app.state.ip_requests.get(client_ip, [])
        request_count = [t for t in request_count if current_time - t < 60]
        
        if len(request_count) >= RATE_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests"
            )
            
        request_count.append(current_time)
        request.app.state.ip_requests[client_ip] = request_count
        return await call_next(request)

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store"
        return response

# Initialize FastAPI app
app = FastAPI(
    title="Blogging API",
    description="A modern API for blog management",
    version="1.0.0",
    docs_url=None,  # We'll customize the docs URL
    redoc_url="/redoc",
    debug=DEBUG
)

# Add state for rate limiting
app.state.ip_requests = {}

# Add security middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY,
    session_cookie=SESSION_COOKIE_NAME,
    max_age=1800,  # 30 minutes
    same_site=settings.SESSION_COOKIE_SAMESITE,
    https_only=settings.SESSION_COOKIE_SECURE
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

# Rate limiting
if ENVIRONMENT != "development":
    app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=TRUSTED_HOSTS
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include all routers
app.include_router(auth.router)
app.include_router(category.router)
app.include_router(comment.router)
app.include_router(like.router)
app.include_router(post.router)
app.include_router(user.router)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        # Verify security configuration
        if ENVIRONMENT != "development" and SECRET_KEY == secrets.token_urlsafe(32):
            logger.warning("Using default SECRET_KEY in non-development environment")
        
        if ENVIRONMENT != "development" and "*" in ALLOWED_ORIGINS:
            logger.warning("Using wildcard CORS origin in non-development environment")
        
        # Create database tables
        model.Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Log startup configuration
        logger.info(f"Starting application in {ENVIRONMENT} mode")
        logger.info(f"Debug mode: {DEBUG}")
        logger.info(f"Rate limit: {RATE_LIMIT} requests per minute")
        logger.info(f"CORS origins: {ALLOWED_ORIGINS}")
        logger.info(f"Trusted hosts: {TRUSTED_HOSTS}")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    try:
        # Close any open connections
        await engine.dispose()
        logger.info("Shutdown completed successfully")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
        raise

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI endpoint."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """Health check endpoint to verify the API is running."""
    security_warnings: List[str] = []
    
    if ENVIRONMENT != "development":
        if SECRET_KEY == secrets.token_urlsafe(32):
            security_warnings.append("Using default SECRET_KEY")
        if "*" in ALLOWED_ORIGINS:
            security_warnings.append("Using wildcard CORS origin")
    
    return {
        "status": "healthy",
        "version": app.version,
        "environment": ENVIRONMENT,
        "debug": DEBUG,
        "security_warnings": security_warnings
    }

@app.get("/", status_code=status.HTTP_200_OK, tags=["Info"])
async def api_info(user: user_dependency = None):
    """API information endpoint."""
    info = {
        "name": app.title,
        "version": app.version,
        "description": app.description,
        "environment": ENVIRONMENT,
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        },
        "auth_required": [
            "/posts/create",
            "/posts/update",
            "/posts/delete",
            "/comments",
            "/likes"
        ]
    }
    
    if user:
        info["user"] = user
    
    return info
