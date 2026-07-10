"""Auth Pydantic schemas."""
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class TokenPayload(BaseModel):
    sub: str
    exp: int
    type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=6)
    confirmPassword: str = Field(min_length=6)


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: Literal["admin", "auditor", "viewer"]
    avatarUrl: str | None = None

    class Config:
        from_attributes = True

    @field_validator("role", mode="before")
    @classmethod
    def _role_to_str(cls, v):
        if hasattr(v, "value"):
            return v.value
        return v


class RefreshRequest(BaseModel):
    refreshToken: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


UserOut.model_rebuild()
TokenResponse.model_rebuild()
