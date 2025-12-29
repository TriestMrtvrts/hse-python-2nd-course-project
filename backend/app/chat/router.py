from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.chat.service import detect_vacancy_with_llm
from datetime import datetime
from app.chat.limits import today_range
from app.llm.prompts import interview_system_prompt
from app.llm.client import qwen_client

from app.auth.deps import get_current_user
from app.db.postgres import get_db
from app.db.deps import get_mongo
from app.chat.schemas import NewChatRequest, MessageRequest
from app.chat.repository import create_chat, get_chat
from app.chat.service import (
    load_questions_for_vacancy,
    generate_greeting,
    detect_vacancy_with_llm,
    generate_questions_for_vacancy,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/new")
async def new_chat(
    user=Depends(get_current_user),
    mongo=Depends(get_mongo),
):
    # лимит 3 интервью в день
    start, end = today_range()
    count = await mongo.chats.count_documents({
        "user_id": str(user.id),
        "created_at": {"$gte": start, "$lt": end},
    })

    if count >= 1000:
        raise HTTPException(
            status_code=429,
            detail="Daily interview limit reached (3)",
        )

    chat = {
        "user_id": str(user.id),
        "vacancy_id": None,
        "vacancy_title": None,
        "questions": [],
        "current_question_index": 0,
        "messages": [],
        "finished": False,
        "created_at": datetime.utcnow(),
    }

    result = await mongo.chats.insert_one(chat)

    return {"chat_id": str(result.inserted_id)}

@router.get("/{chat_id}")
async def get_chat_state(
    chat_id: str,
    user=Depends(get_current_user),
    mongo=Depends(get_mongo),
):
    chat = await get_chat(mongo, chat_id, str(user.id))
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat




from datetime import datetime
from app.chat.utils import (
    get_current_question,
    mark_question_used,
    apply_evaluation,
)
from app.chat.service import (
    generate_hint,
    generate_answer,
    evaluate_chat,
)


@router.post("/{chat_id}/message")
async def send_message(
    chat_id: str,
    data: MessageRequest,
    user=Depends(get_current_user),
    mongo=Depends(get_mongo),
):
    chat = await get_chat(mongo, chat_id, str(user.id))
    if not chat or chat.get("finished"):
        raise HTTPException(status_code=400, detail="Invalid chat")

    user_text = data.content.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Empty message")

    # 1️⃣ сохраняем сообщение пользователя
    await mongo.chats.update_one(
        {"_id": chat_id},
        {
            "$push": {
                "messages": {
                    "role": "user",
                    "content": user_text,
                    "timestamp": datetime.utcnow(),
                }
            }
        },
    )

    # 2️⃣ собираем историю диалога
    history = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in chat.get("messages", [])
    )

    # 3️⃣ формируем prompt
    prompt = f"""
Ты — опытный технический интервьюер.
Веди интервью строго и профессионально.
Задавай уточняющие вопросы.
Не объясняй, что ты ИИ.

История диалога:
{history}

user: {user_text}
assistant:
""".strip()

    # 4️⃣ вызываем LLM (ОДИН раз)
    reply = await qwen_client.generate(prompt)

    reply = (reply or "").strip()
    if not reply:
        reply = "Продолжим интервью. Расскажи подробнее."

    # 5️⃣ сохраняем ответ ассистента
    await mongo.chats.update_one(
        {"_id": chat_id},
        {
            "$push": {
                "messages": {
                    "role": "assistant",
                    "content": reply,
                    "timestamp": datetime.utcnow(),
                }
            }
        },
    )

    # 6️⃣ возвращаем ответ фронту
    return {"reply": reply}


@router.post("/{chat_id}/hint")
async def get_hint(
    chat_id: str,
    user=Depends(get_current_user),
    mongo=Depends(get_mongo),
):
    chat = await get_chat(mongo, chat_id, str(user.id))
    question = get_current_question(chat["questions"])

    if not question:
        raise HTTPException(status_code=400, detail="No active question")

    hint = await generate_hint(
        question["text"],
        context=" ".join(m["content"] for m in chat["messages"] if m["role"] == "user"),
    )

    await mongo.chats.update_one(
        {"_id": chat_id},
        {
            "$push": {
                "messages": {
                    "role": "assistant",
                    "content": hint,
                    "timestamp": datetime.utcnow(),
                }
            }
        },
    )

    return {"hint": hint}


@router.post("/{chat_id}/answer")
async def get_answer(
    chat_id: str,
    user=Depends(get_current_user),
    mongo=Depends(get_mongo),
):
    chat = await get_chat(mongo, chat_id, str(user.id))
    question = get_current_question(chat["questions"])

    if not question:
        raise HTTPException(status_code=400, detail="No active question")

    answer = await generate_answer(question["text"])

    await mongo.chats.update_one(
        {"_id": chat_id},
        {
            "$push": {
                "messages": {
                    "role": "assistant",
                    "content": answer,
                    "timestamp": datetime.utcnow(),
                }
            }
        },
    )

    return {"answer": answer}


@router.post("/{chat_id}/finish")
async def finish_chat(
    chat_id: str,
    user=Depends(get_current_user),
    mongo=Depends(get_mongo),
):
    chat = await get_chat(mongo, chat_id, str(user.id))
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    history = "\n".join(
        f"{m['role']}: {m['content']}" for m in chat["messages"]
    )

    evaluation = await evaluate_chat(history)
    apply_evaluation(chat["questions"], evaluation)

    await mongo.chats.update_one(
        {"_id": chat_id},
        {
            "$set": {
                "questions": chat["questions"],
                "finished": True,
            }
        },
    )

    return {"evaluation": evaluation}


@router.post("/{chat_id}/retry-mistakes")
async def retry_mistakes(
    chat_id: str,
    user=Depends(get_current_user),
    mongo=Depends(get_mongo),
):
    chat = await get_chat(mongo, chat_id, str(user.id))
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    for q in chat["questions"]:
        if q["mistakes"]:
            q["used"] = False
            q["score"] = None

    await mongo.chats.update_one(
        {"_id": chat_id},
        {
            "$set": {
                "questions": chat["questions"],
                "finished": False,
                "messages": [],
            }
        },
    )

    return {"status": "restarted_only_mistakes"}


@router.delete("/clear")
async def clear_chats(
    user=Depends(get_current_user),
    mongo=Depends(get_mongo),
):
    await mongo.chats.delete_many({"user_id": str(user.id)})
    return {"status": "cleared"}



@router.get("")
async def list_chats(
    user=Depends(get_current_user),
    mongo=Depends(get_mongo),
):
    chats = await mongo.chats.find(
        {"user_id": str(user.id)},
        {
            "vacancy_title": 1,
            "created_at": 1,
            "finished": 1,
        }
    ).sort("created_at", -1).to_list(100)

    return [
        {
            "id": str(c["_id"]),
            "title": c.get("vacancy_title"),
            "created_at": c["created_at"],
            "finished": c["finished"],
        }
        for c in chats
    ]