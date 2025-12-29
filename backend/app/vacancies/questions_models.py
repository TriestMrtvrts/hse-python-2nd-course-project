import uuid
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    vacancy_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vacancies.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )