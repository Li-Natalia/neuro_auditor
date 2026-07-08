"""API routers package."""
from fastapi import APIRouter

from app.api.routes import analysis, auth, chat, documents, reports


def get_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(auth.router, prefix="/auth", tags=["auth"])
    router.include_router(documents.router, prefix="/documents", tags=["documents"])
    router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
    router.include_router(reports.router, prefix="/reports", tags=["reports"])
    router.include_router(chat.router, prefix="/chat", tags=["chat"])
    return router
