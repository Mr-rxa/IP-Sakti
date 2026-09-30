from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.router import api_v1_router
from app.db.init_db import init_db
from app.core.exceptions import IPSaktiException
from app.core.disclaimer import DISCLAIMER_TEXT
from app.utils.logging import logger
from app.security.rate_limit import rate_limit_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing IP-SAKTI Sahayak database and seed data...")
    init_db()
    logger.info("Database initialized successfully.")
    yield
    logger.info("Shutting down IP-SAKTI Sahayak application.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Multilingual RAG Assistant for Ayurveda IPR & Regulatory Guidance (SIH26045)",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(rate_limit_middleware)

@app.middleware("http")
async def request_size_middleware(request: Request, call_next):
    content_length = request.headers.get("content-length")
    try:
        oversized = content_length and int(content_length) > settings.MAX_REQUEST_BODY_BYTES
    except ValueError:
        oversized = True
    if oversized:
        return JSONResponse(
            status_code=413,
            content={"error_code": "REQUEST_TOO_LARGE", "message": "Request body exceeds the configured limit."},
        )
    return await call_next(request)

# Global custom exception handler adhering to 05_API_Specification Section 10
@app.exception_handler(IPSaktiException)
async def ipsakti_exception_handler(request: Request, exc: IPSaktiException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s: %s", request.url.path, exc.__class__.__name__, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later."
        }
    )

# Inject persistent disclaimer header into all HTTP responses
@app.middleware("http")
async def disclaimer_header_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Legal-Disclaimer"] = "Information only - not legal advice"
    return response

# Mount v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to IP-SAKTI Sahayak API",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_PREFIX,
        "disclaimer": DISCLAIMER_TEXT
    }
