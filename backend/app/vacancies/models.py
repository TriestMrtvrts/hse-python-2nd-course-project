import uuid
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )