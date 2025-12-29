from datetime import datetime
from bson import ObjectId
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase


def serialize_chat(chat: dict) -> dict:
    chat["chat_id"] = str(chat["_id"])
    del chat["_id"]
    return chat


async def create_chat(
    mongo: AsyncIOMotorDatabase,
    user_id: str,
    vacancy_id: str,
    vacancy_title: str,
    questions: List[dict],
    questions_version: int,
):
    doc = {
        "user_id": user_id,
        "vacancy_id": vacancy_id,
        "vacancy_title": vacancy_title,
        "questions": questions,
        "messages": [],
        "finished": False,
        "questions_version": questions_version,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await mongo.chats.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_chat(doc)


async def get_chat(
    mongo: AsyncIOMotorDatabase,
    chat_id: str,
    user_id: str,
):
    chat = await mongo.chats.find_one(
        {"_id": ObjectId(chat_id), "user_id": user_id}
    )
    return serialize_chat(chat) if chat else None