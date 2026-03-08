from collections.abc import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.base.base_accessor import BaseAccessor
from app.game.models import (
    AnswerModel,
    QuestionModel,
    ThemeModel,
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
