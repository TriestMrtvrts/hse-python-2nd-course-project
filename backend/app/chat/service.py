from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.vacancies.models import Vacancy
from app.vacancies.questions_models import Question
from app.llm.client import qwen_client
from app.llm.prompts import (
    interview_greeting,
    hint_prompt,
    answer_prompt,
    evaluation_prompt,
)


async def load_questions_for_vacancy(
    db: AsyncSession,
    vacancy_title: str,
):
    vacancy = (
        await db.execute(
            select(Vacancy).where(Vacancy.title == vacancy_title)
        )
    ).scalar_one_or_none()

    if not vacancy:
        raise ValueError("Vacancy not found")

    questions = (
        await db.execute(
            select(Question)
            .where(Question.vacancy_id == vacancy.id)
            .order_by(Question.version.desc())
        )
    ).scalars().all()

    if not questions:
        raise ValueError("No questions for vacancy")

    latest_version = max(q.version for q in questions)

    questions_state = [
        {
            "question_id": str(q.id),
            "text": q.question,
            "used": False,
            "mistakes": False,
            "score": None,
        }
        for q in questions
        if q.version == latest_version
    ]

    return vacancy, questions_state, latest_version


async def generate_greeting(vacancy_title: str) -> str:
    prompt = interview_greeting(vacancy_title)
    return await qwen_client.generate(prompt)


from app.chat.utils import get_current_question


async def generate_hint(question: str, context: str) -> str:
    prompt = hint_prompt(question, context)
    return await qwen_client.generate(prompt)


async def generate_answer(question: str) -> str:
    prompt = answer_prompt(question)
    return await qwen_client.generate(prompt)


async def evaluate_chat(chat_history: str) -> list[dict]:
    prompt = evaluation_prompt(chat_history)
    raw = await qwen_client.generate(prompt)

    import json

    try:
        return json.loads(raw)
    except Exception:
        raise ValueError("LLM returned invalid JSON")
    

async def detect_vacancy_with_llm(user_message: str, db: AsyncSession):
    vacancies = (await db.execute(select(Vacancy))).scalars().all()
    titles = [v.title for v in vacancies]

    prompt = detect_vacancy_prompt(user_message, titles)
    detected = await qwen_client.generate(prompt)

    for v in vacancies:
        if v.title.lower() in detected.lower():
            return v

    raise ValueError("Vacancy not detected")


from sqlalchemy import select
from app.vacancies.models import Vacancy
from app.llm.prompts import detect_vacancy_prompt
from app.llm.client import qwen_client


async def detect_vacancy_with_llm(user_message: str, db):
    result = await db.execute(select(Vacancy))
    vacancies = result.scalars().all()

    if not vacancies:
        raise ValueError("No vacancies in database")

    titles = [v.title for v in vacancies]

    prompt = detect_vacancy_prompt(user_message, titles)

    detected = await qwen_client.generate(prompt)

    # простой, но надёжный матч
    detected_lower = detected.lower()
    for v in vacancies:
        if v.title.lower() in detected_lower:
            return v

    # fallback — первая вакансия (чтобы НЕ падать)
    return vacancies[0]


from app.llm.client import qwen_client
from app.llm.prompts import generate_questions_prompt


async def generate_questions_for_vacancy(vacancy_title: str) -> list[dict]:
    prompt = generate_questions_prompt(vacancy_title)
    raw = await qwen_client.generate(prompt)

    questions = []
    for line in raw.split("\n"):
        line = line.strip("-• ").strip()
        if line:
            questions.append({
                "text": line,
                "used": False,
                "mistakes": False,
                "score": None,
            })

    return questions