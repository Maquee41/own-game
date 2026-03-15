from datetime import UTC, datetime

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.game.types import MatchStatus, RoomStatus
from app.store.database.sqlalchemy_base import BaseModel


class AnswerModel(BaseModel):
    __tablename__ = 'answers'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    is_correct: Mapped[bool] = mapped_column(nullable=False)
    question_id: Mapped[int] = mapped_column(
        ForeignKey(
            'questions.id',
            ondelete='CASCADE',
        ),
        nullable=False,
    )
    question: Mapped['QuestionModel'] = relationship(back_populates='answers')


class ThemeModel(BaseModel):
    __tablename__ = 'themes'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    questions: Mapped[list['QuestionModel']] = relationship(
        back_populates='theme',
        cascade='all, delete-orphan',
    )


class QuestionModel(BaseModel):
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    theme_id: Mapped[int] = mapped_column(
        ForeignKey('themes.id', ondelete='CASCADE'),
        nullable=False,
    )
    theme: Mapped['ThemeModel'] = relationship(back_populates='questions')
    answers: Mapped[list['AnswerModel']] = relationship(
        back_populates='question',
        cascade='all, delete-orphan',
    )


class MatchModel(BaseModel):
    __tablename__ = 'matches'

    room_id: Mapped[int] = mapped_column(
        ForeignKey('rooms.id', ondelete='CASCADE'),
        nullable=False,
    )
    start_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
    end_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[MatchStatus] = mapped_column(String(10))
    results: Mapped[dict[str, int]] = mapped_column(JSON, nullable=True)


class RoomModel(BaseModel):
    __tablename__ = 'rooms'

    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    status: Mapped[RoomStatus] = mapped_column(String(10))
    state: Mapped[dict] = mapped_column(JSON, default={})


class UserModel(BaseModel):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(unique=True, nullable=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    score: Mapped[int] = mapped_column(default=0)
