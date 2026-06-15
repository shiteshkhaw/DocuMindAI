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
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

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

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

