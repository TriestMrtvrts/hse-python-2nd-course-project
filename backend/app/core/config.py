from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Interview Trainer"
    DEBUG: bool = True

    POSTGRES_DSN: str
    MONGO_DSN: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    LLM_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()