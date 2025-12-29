from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str
    preferred_language: str = "ru"


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str