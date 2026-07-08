"""Authentication business logic."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise ValueError("Пользователь с таким email уже существует")
    user = User(
        email=data.email,
        name=data.name,
        hashed_password=hash_password(data.password),
        role=UserRole.viewer,
    )
    db.add(user)
    await db.flush()
    return user


async def authenticate(db: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Неверный email или пароль")
    if not user.is_active:
        raise ValueError("Учётная запись отключена")
    return user


def issue_tokens(user: User) -> dict:
    return {
        "accessToken": create_access_token(user.id, {"role": user.role.value}),
        "refreshToken": create_refresh_token(user.id),
        "tokenType": "bearer",
    }


def refresh_access_token(refresh_token: str) -> str:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise ValueError("Недействительный refresh-токен")
    return create_access_token(payload["sub"])


async def reset_password_request(db: AsyncSession, email: str) -> str:
    user = await get_user_by_email(db, email)
    # Always return the same message to avoid user enumeration
    if user:
        # TODO: send email with reset link / set reset token
        pass
    return "Если учётная запись существует, инструкции отправлены на email"
