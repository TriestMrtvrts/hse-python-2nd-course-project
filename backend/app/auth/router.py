from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.postgres import get_db
from app.auth.passwords import validate_password
from app.users.models import User
from app.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.auth.security import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        validate_password(data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    result = await db.execute(
        select(User).where(User.username == data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        preferred_language=data.preferred_language,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.username == data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )