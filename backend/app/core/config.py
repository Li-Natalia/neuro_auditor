"""Application configuration via pydantic-settings."""
from functools import lru_cache
from typing import List

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Committed default — must never be used in production.
INSECURE_DEFAULT_SECRET = "change-me-to-a-long-random-secret-key-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "Нейроаудитор"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_API_PREFIX: str = "/api"

    # Run `alembic upgrade head` on application startup (disabled in tests).
    RUN_MIGRATIONS_ON_STARTUP: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://finauditor:finauditor@localhost:5432/finauditor"
    DATABASE_URL_SYNC: str = "postgresql://finauditor:finauditor@localhost:5432/finauditor"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Security
    SECRET_KEY: str = "change-me-to-a-long-random-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Files
    UPLOAD_DIR: str = "./media/uploads"
    REPORT_DIR: str = "./media/reports"
    MAX_UPLOAD_SIZE_MB: int = 20
    ALLOWED_EXTENSIONS: str = "xlsx,xls"

    # --- Yandex AI Studio: YandexGPT via the OpenAI SDK (Responses API) ---
    AI_BASE_URL: str = "https://ai.api.cloud.yandex.net/v1"
    AI_YC_API_KEY: str = ""
    AI_YC_FOLDER_ID: str = ""
    # Model name inside the folder; composed into gpt://<folder>/<model> (or pass a full gpt:// URI)
    AI_MODEL: str = "yandexgpt/latest"
    AI_TEMPERATURE: float = 0.2
    AI_MAX_TOKENS: int = 2000  # mapped to Responses API `max_output_tokens`
    AI_TIMEOUT_SECONDS: float = 60

    # Code Interpreter chat mode (Files API + Responses API tool). Off by default in code;
    # .env.example enables it and points AI_CI_MODEL at a model known to support the tool.
    AI_CODE_INTERPRETER_ENABLED: bool = False
    AI_CI_MODEL: str = ""  # empty -> AI_MODEL
    AI_CI_FILE_PURPOSE: str = "user_data"
    # Code Interpreter answers take 1–3 minutes (Qwen + several code executions)
    AI_CI_TIMEOUT_SECONDS: float = 300

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors(cls, v: str) -> str:
        return v

    @model_validator(mode="after")
    def _guard_production_secret(self) -> "Settings":
        """Refuse to boot in production with a weak/default JWT secret."""
        if self.APP_ENV == "production":
            if (
                not self.SECRET_KEY
                or self.SECRET_KEY == INSECURE_DEFAULT_SECRET
                or len(self.SECRET_KEY) < 32
            ):
                raise ValueError(
                    "SECRET_KEY должен быть задан в production: не менее 32 символов и не "
                    "равен значению по умолчанию. Установите переменную окружения SECRET_KEY."
                )
        return self

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [e.strip().lower() for e in self.ALLOWED_EXTENSIONS.split(",") if e.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
