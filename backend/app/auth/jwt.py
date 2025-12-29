import uuid
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings


def create_access_token(user_id: uuid.UUID) -> str:
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": datetime.utcnow()
        + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: uuid.UUID) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.utcnow()
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )