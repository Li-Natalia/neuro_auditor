"""FastAPI application entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.middleware.cors import setup_cors
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.api.routes import get_api_router
from app.core.config import settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield
    # Shutdown
    from app.core.redis import close_redis

    await close_redis()


app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description="Анализ финансовой отчетности, выявление рисков и AI-чат-бот",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

setup_cors(app)
app.add_middleware(RateLimitMiddleware)

app.include_router(get_api_router(), prefix=settings.APP_API_PREFIX)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}


@app.get("/", tags=["root"])
async def root():
    return {"app": settings.APP_NAME, "docs": "/docs"}
