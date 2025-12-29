from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class NewChatRequest(BaseModel):
    vacancy_title: str


class MessageRequest(BaseModel):
    content: str


class ChatMessage(BaseModel):
    role: str  # user | assistant | system
    content: str
    timestamp: datetime


class QuestionState(BaseModel):
    question_id: str
    text: str
    used: bool = False
    mistakes: bool = False
    score: Optional[int] = None


class ChatResponse(BaseModel):
    chat_id: str
    messages: List[ChatMessage]
    questions: List[QuestionState]
    finished: bool