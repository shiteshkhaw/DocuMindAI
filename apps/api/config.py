from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Any
from pathlib import Path
import json

# Resolve .env relative to this file so it's found regardless of launch CWD
_ENV_FILE = Path(__file__).parent / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "DocuMind AI"
    # Auth
    JWT_SECRET: str = "super-secret-key-for-dev"
    GOOGLE_CLIENT_ID: str = ""
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://neondb_owner:password@c-2.ap-southeast-1.aws.neon.tech/neondb",
        description="Asyncpg database connection string"
    )
    CORS_ORIGINS: Any = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "https://docu-mind-ai-web.vercel.app",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        origins: list[str] = []
        if isinstance(v, str):
            v = v.strip()
            if v:
                if (v.startswith("[") and v.endswith("]")) or (v.startswith("{") and v.endswith("}")):
                    try:
                        parsed = json.loads(v)
                        if isinstance(parsed, list):
                            origins = [str(x).strip().rstrip("/") for x in parsed if str(x).strip()]
                    except Exception:
                        pass
                if not origins:
                    # Robust split by comma for plain URLs or single/double quoted items
                    origins = [x.strip().strip("'").strip('"').rstrip("/") for x in v.split(",") if x.strip()]
        elif isinstance(v, (list, tuple, set)):
            origins = [str(x).strip().rstrip("/") for x in v if str(x).strip()]
        else:
            origins = [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:3001",
                "https://docu-mind-ai-web.vercel.app",
            ]

        # Always guarantee canonical production frontend URL is present in CORS origins
        canonical = "https://docu-mind-ai-web.vercel.app"
        if canonical not in origins:
            origins.append(canonical)
        return origins

    MAX_FILE_SIZE_MB: int = 10

    # AI Pipeline Configurations
    EMBEDDING_PROVIDER: str = "mock"  # Options: mock, openai, gemini, huggingface
    VECTOR_STORE_PROVIDER: str = "chroma"  # Options: chroma

    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    HF_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    
    # Chroma Configs
    CHROMA_SERVER_HOST: str | None = None
    CHROMA_SERVER_PORT: str = "8000"
    CHROMA_PERSIST_DIRECTORY: str | None = None
    CHROMA_API_KEY: str | None = None
    CHROMA_TENANT: str | None = None
    CHROMA_DATABASE: str | None = None

    # ── Upstash Redis ─────────────────────────────────────────────────────
    UPSTASH_REDIS_URL: str | None = None
    UPSTASH_REDIS_REST_TOKEN: str | None = None

    # ── Supabase Storage ──────────────────────────────────────────────────
    SUPABASE_URL: str | None = None
    SUPABASE_ANON_KEY: str | None = None
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    SUPABASE_STORAGE_BUCKET: str = "documind-vault"

    # ── Sentry Monitoring ─────────────────────────────────────────────────
    SENTRY_DSN: str | None = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1

    # ── Resend Email ──────────────────────────────────────────────────────
    RESEND_API_KEY: str | None = None
    EMAIL_FROM: str = "DocuMind AI <noreply@documind.ai>"

    # ── Dramatiq Workers ──────────────────────────────────────────────────
    DRAMATIQ_BROKER_URL: str | None = None
    RUN_WORKERS_IN_PROCESS: bool = False

    @property
    def effective_broker_url(self) -> str | None:
        return self.DRAMATIQ_BROKER_URL or self.UPSTASH_REDIS_URL

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

