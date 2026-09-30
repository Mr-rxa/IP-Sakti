from typing import List, Union, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import json
from urllib.parse import quote_plus

class Settings(BaseSettings):
    PROJECT_NAME: str = "IP-SAKTI Sahayak Backend"
    API_V1_PREFIX: str = "/api/v1"
    ENV: str = "development"
    DEBUG: bool = True
    MAX_REQUEST_BODY_BYTES: int = 262144
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Database
    DATABASE_URL: Optional[str] = None

    # Supabase Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_DB_HOST: Optional[str] = None
    SUPABASE_DB_USER: str = "postgres"
    SUPABASE_DB_PASSWORD: Optional[str] = None
    SUPABASE_DB_NAME: str = "postgres"
    SUPABASE_DB_PORT: int = 6543
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None

    # Pinecone Vector DB Configuration
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_INDEX_NAME: str = "ip-sakti-corpus"
    PINECONE_ENVIRONMENT: str = "us-east-1"

    # JWT Authentication
    JWT_SECRET: str = "ip-shakti-secret-key-ayush-2026-supersecure"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # LLM Configuration
    LLM_PROVIDER: str = "mock"  # mock | openai | local | bhashini | gemini
    OPENAI_API_KEY: str = "mock-key"
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: Optional[str] = None

    # Translation provider. "none" fails closed; "http" requires an explicitly configured endpoint.
    TRANSLATION_PROVIDER: str = "none"
    TRANSLATION_PROVIDER_URL: Optional[str] = None
    TRANSLATION_PROVIDER_API_KEY: Optional[str] = None

    # RAG Service Integration URL (microservice or integrated pipeline)
    RAG_SERVICE_URL: str = "http://127.0.0.1:8001/api/v1"

    # Retrieval & Thresholds
    VECTOR_DB_TYPE: str = "pinecone"  # pinecone | chroma | in-memory
    CONFIDENCE_THRESHOLD_LOW: float = 0.40
    CONFIDENCE_THRESHOLD_HIGH: float = 0.75

    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v

    CORPUS_VERSION: str = "1.0.0-202608"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

if not settings.DATABASE_URL and settings.SUPABASE_DB_HOST and settings.SUPABASE_DB_PASSWORD:
    settings.DATABASE_URL = (
        f"postgresql+psycopg2://{quote_plus(settings.SUPABASE_DB_USER)}:"
        f"{quote_plus(settings.SUPABASE_DB_PASSWORD)}@{settings.SUPABASE_DB_HOST}:"
        f"{settings.SUPABASE_DB_PORT}/{settings.SUPABASE_DB_NAME}"
    )
