from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.security import decode_token
from app.domain.identity.schemas import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_token(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    try:
        payload = decode_token(token)
        return TokenPayload.model_validate(payload)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
