"""PromptForge AI - FastAPI Backend Application."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import CORS_ORIGINS, RATE_LIMIT
from database import init_db
from api.auth import router as auth_router
from api.routes import router as api_router
from api.security_routes import router as security_router

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])

app = FastAPI(
    title="PromptForge AI",
    description="AI-powered prompt engineering platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


# Routes
app.include_router(auth_router)
app.include_router(api_router)
app.include_router(security_router)


@app.on_event("startup")
def startup():
    """Initialize the database on startup."""
    init_db()


@app.get("/")
def root():
    return {
        "name": "PromptForge AI",
        "version": "1.0.0",
        "docs": "/docs",
    }
