from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.core.config import settings
from app.auth.router import router as auth_router

from app.chat.router import router as chat_router


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router)

# healthcheck
@app.get("/health")
async def healthcheck():
    return {"status": "ok"}

# подключаем роутеры ПОСЛЕ создания app
app.include_router(auth_router)