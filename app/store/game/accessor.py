from collections.abc import Iterable, Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.base.base_accessor import BaseAccessor
from app.game.models import (
    AnswerModel,
    MatchModel,
    MatchStatus,
    QuestionModel,
    RoomModel,
    RoomStatus,
    ThemeModel,
    UserModel,
)


class GameAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> ThemeModel:
        async with self.app.database.session() as session:
            theme_model = ThemeModel(title=title)
            session.add(theme_model)
            await session.commit()
            return theme_model

    async def get_theme_by_title(self, title: str) -> ThemeModel | None:
        stmt = select(ThemeModel).where(ThemeModel.title == title)
        async with self.app.database.session() as session:
            theme = await session.scalars(stmt)
            return theme.one_or_none()

    async def get_theme_by_id(self, id_: int) -> ThemeModel | None:
        stmt = select(ThemeModel).where(ThemeModel.id == id_)
        async with self.app.database.session() as session:
            theme = await session.scalars(stmt)
            return theme.one_or_none()

    async def list_themes(self) -> Sequence[ThemeModel]:
        stmt = select(ThemeModel)
        async with self.app.database.session() as session:
            themes = await session.scalars(stmt)
            return themes.all()

    async def create_question(
        self, title: str, theme_id: int, answers: Iterable[AnswerModel]
    ) -> QuestionModel:
        async with self.app.database.session() as session:
            question_model = QuestionModel(
                title=title,
                theme_id=theme_id,
                answers=answers,
            )
            session.add(question_model)
            await session.commit()
            return question_model

    async def get_question_by_title(self, title: str) -> QuestionModel | None:
        stmt = select(QuestionModel).where(QuestionModel.title == title)
        async with self.app.database.session() as session:
            question = await session.scalars(stmt)
            return question.first()

    async def list_questions(
        self, theme_id: int | None = None
    ) -> Sequence[QuestionModel]:
        stmt = select(QuestionModel).options(selectinload(QuestionModel.answers))
        if theme_id:
            stmt = stmt.where(QuestionModel.theme_id == theme_id)

        async with self.app.database.session() as session:
            questions = await session.scalars(stmt)
            return questions.all()

    async def create_room(
        self,
        chat_id: int,
        status: RoomStatus,
        theme_id: int,
        state: dict,
    ) -> RoomModel:
        async with self.app.database.session() as session:
            room_model = RoomModel(
                chat_id=chat_id,
                status=status.value,
                theme_id=theme_id,
                state=state,
            )
            session.add(room_model)
            await session.commit()
            return room_model

    async def create_match(
        self,
        room_id: int,
        winner_id: int,
        start_at: datetime,
        end_at: datetime,
        status: MatchStatus,
        users: Iterable[UserModel],
        results: dict[str, int],
    ) -> MatchModel:
        async with self.app.database.session() as session:
            match_model = MatchModel(
                room_id=room_id,
                winner_id=winner_id,
                start_at=start_at,
                end_at=end_at,
                status=status.value,
                users=users,
                results=results,
            )
            session.add(match_model)
            await session.commit()
            return match_model

    async def create_user(self, username: str, tg_id: int, score: int) -> UserModel:
        async with self.app.database.session() as session:
            user_model = UserModel(
                username=username,
                tg_id=tg_id,
                score=score,
            )
            session.add(user_model)
            await session.commit()
            return user_model

    async def get_user_by_tg(self, tg_id: int) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.tg_id == tg_id)
        async with self.app.database.session() as session:
            user = await session.scalars(stmt)
            return user.first()
