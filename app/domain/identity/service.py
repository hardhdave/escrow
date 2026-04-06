from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.domain.identity.models import User
from app.domain.identity.schemas import LoginRequest, RegisterRequest, TokenResponse


class IdentityService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def register(self, payload: RegisterRequest) -> TokenResponse:
        existing = self.db.scalar(select(User).where(User.email == payload.email))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user = User(email=payload.email, password_hash=hash_password(payload.password), role=payload.role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return TokenResponse(access_token=create_access_token(user.id, user.role))

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.db.scalar(select(User).where(User.email == payload.email))
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return TokenResponse(access_token=create_access_token(user.id, user.role))
