from collections.abc import Iterable, Sequence
from datetime import datetime

from sqlalchemy import delete, func, select, update
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
from app.game.schemas import Player, RoomState


class GameAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> ThemeModel:
        async with self.app.database.session() as session:
            theme_model = ThemeModel(title=title)
            session.add(theme_model)
            await session.commit()
            await session.refresh(theme_model)
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
        self,
        title: str,
        theme_id: int,
        answers: Iterable[AnswerModel],
    ) -> QuestionModel:
        async with self.app.database.session() as session:
            question_model = QuestionModel(
                title=title,
                theme_id=theme_id,
                answers=list(answers),
            )
            session.add(question_model)
            await session.commit()
            await session.refresh(question_model)
            return question_model

    async def get_question_by_title(self, title: str) -> QuestionModel | None:
        stmt = (
            select(QuestionModel)
            .where(QuestionModel.title == title)
            .options(selectinload(QuestionModel.answers))
        )
        async with self.app.database.session() as session:
            question = await session.scalars(stmt)
            return question.first()

    async def get_question_by_id(self, id_: int) -> QuestionModel | None:
        stmt = (
            select(QuestionModel)
            .where(QuestionModel.id == id_)
            .options(selectinload(QuestionModel.answers))
        )
        async with self.app.database.session() as session:
            question = await session.scalars(stmt)
            return question.one_or_none()

    async def list_questions(
        self,
        theme_id: int | None = None,
    ) -> Sequence[QuestionModel]:
        stmt = select(QuestionModel).options(selectinload(QuestionModel.answers))
        if theme_id is not None:
            stmt = stmt.where(QuestionModel.theme_id == theme_id)

        async with self.app.database.session() as session:
            questions = await session.scalars(stmt)
            return questions.all()

    async def get_random_questions(
        self,
        theme_id: int,
        limit: int,
    ) -> Sequence[QuestionModel]:
        stmt = (
            select(QuestionModel)
            .where(QuestionModel.theme_id == theme_id)
            .options(selectinload(QuestionModel.answers))
            .order_by(func.random())
            .limit(limit)
        )
        async with self.app.database.session() as session:
            questions = await session.scalars(stmt)
            return questions.all()

    async def create_room(
        self,
        chat_id: int,
        status: RoomStatus,
        state: dict,
    ) -> RoomModel:
        async with self.app.database.session() as session:
            room_model = RoomModel(
                chat_id=chat_id,
                status=status.value,
                state=state,
            )
            session.add(room_model)
            await session.commit()
            await session.refresh(room_model)
            return room_model

    async def get_room_by_chat_id(self, chat_id: int) -> RoomModel | None:
        stmt = select(RoomModel).where(RoomModel.chat_id == chat_id)
        async with self.app.database.session() as session:
            room = await session.scalars(stmt)
            return room.one_or_none()

    async def get_room_state(self, chat_id: int) -> RoomState | None:
        room = await self.get_room_by_chat_id(chat_id)
        if room is None:
            return None
        return RoomState.model_validate(room.state or {})

    async def save_room_state(self, chat_id: int, state: RoomState) -> None:
        stmt = (
            update(RoomModel)
            .where(RoomModel.chat_id == chat_id)
            .values(state=state.model_dump(mode='json'))
        )
        async with self.app.database.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def update_room_status(self, chat_id: int, status: RoomStatus) -> None:
        stmt = (
            update(RoomModel)
            .where(RoomModel.chat_id == chat_id)
            .values(status=status.value)
        )
        async with self.app.database.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def update_room_theme(self, chat_id: int, theme_id: int | None) -> None:
        stmt = (
            update(RoomModel)
            .where(RoomModel.chat_id == chat_id)
            .values(theme_id=theme_id)
        )
        async with self.app.database.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def delete_room(self, chat_id: int) -> None:
        stmt = delete(RoomModel).where(RoomModel.chat_id == chat_id)
        async with self.app.database.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def room_exists(self, chat_id: int) -> bool:
        room = await self.get_room_by_chat_id(chat_id)
        return room is not None

    async def create_match(
        self,
        room_id: int,
        start_at: datetime,
        end_at: datetime | None,
        status: MatchStatus,
        results: dict[str, int] | None = None,
    ) -> MatchModel:
        async with self.app.database.session() as session:
            match_model = MatchModel(
                room_id=room_id,
                start_at=start_at,
                end_at=end_at,
                status=status.value,
                results=results,
            )
            session.add(match_model)
            await session.commit()
            await session.refresh(match_model)
            return match_model

    async def finish_match(
        self,
        room_id: int,
        end_at: datetime,
        status: MatchStatus,
        results: dict[str, int],
    ) -> None:
        stmt = (
            update(MatchModel)
            .where(MatchModel.room_id == room_id)
            .values(
                end_at=end_at,
                status=status.value,
                results=results,
            )
        )
        async with self.app.database.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_match_by_room_id(self, room_id: int) -> MatchModel | None:
        stmt = select(MatchModel).where(MatchModel.room_id == room_id)
        async with self.app.database.session() as session:
            match = await session.scalars(stmt)
            return match.one_or_none()

    async def create_user(self, tg_id: int, username: str | None = None) -> UserModel:
        async with self.app.database.session() as session:
            user_model = UserModel(
                username=username,
                tg_id=tg_id,
            )
            session.add(user_model)
            await session.commit()
            await session.refresh(user_model)
            return user_model

    async def get_user_by_tg(self, tg_id: int) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.tg_id == tg_id)
        async with self.app.database.session() as session:
            user = await session.scalars(stmt)
            return user.first()

    async def get_or_create_user(self, tg_id: int, username: str | None) -> UserModel:
        user = await self.get_user_by_tg(tg_id)
        if user is not None:
            return user

        return await self.create_user(
            tg_id=tg_id,
            username=username,
        )

    async def update_user_score(self, tg_id: int, delta: int) -> None:
        async with self.app.database.session() as session:
            user = await session.scalar(
                select(UserModel).where(UserModel.tg_id == tg_id)
            )
            if user is None:
                return

            user.score += delta
            await session.commit()

    async def set_user_score(self, tg_id: int, score: int) -> None:
        stmt = update(UserModel).where(UserModel.tg_id == tg_id).values(score=score)
        async with self.app.database.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def add_player_to_room(self, chat_id: int, tg_id: int) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        if any(player.tg_id == tg_id for player in state.players):
            return state

        state.players.append(Player(tg_id=tg_id))
        await self.save_room_state(chat_id, state)
        return state

    async def remove_player_from_room(
        self, chat_id: int, tg_id: int
    ) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        state.players = [player for player in state.players if player.tg_id != tg_id]
        await self.save_room_state(chat_id, state)
        return state

    async def confirm_player(self, chat_id: int, tg_id: int) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        for player in state.players:
            if player.tg_id == tg_id:
                player.confirmed = True
                break

        await self.save_room_state(chat_id, state)
        return state

    async def reset_players_confirmed(self, chat_id: int) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        for player in state.players:
            player.confirmed = False

        await self.save_room_state(chat_id, state)
        return state

    async def set_player_score_in_room(
        self,
        chat_id: int,
        tg_id: int,
        score: int,
    ) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        for player in state.players:
            if player.tg_id == tg_id:
                player.score = score
                break

        await self.save_room_state(chat_id, state)
        return state

    async def increment_player_score_in_room(
        self,
        chat_id: int,
        tg_id: int,
        delta: int,
    ) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        for player in state.players:
            if player.tg_id == tg_id:
                player.score += delta
                break

        await self.save_room_state(chat_id, state)
        return state

    async def set_room_message_id(
        self, chat_id: int, message_id: int
    ) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        state.message_id = message_id
        await self.save_room_state(chat_id, state)
        return state

    async def set_room_question_ids(
        self,
        chat_id: int,
        question_ids: list[int],
    ) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        state.question_ids = question_ids
        await self.save_room_state(chat_id, state)
        return state

    async def set_current_question(
        self,
        chat_id: int,
        question_id: int | None,
    ) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        state.current_question_id = question_id
        await self.save_room_state(chat_id, state)
        return state

    async def set_question_opened_at(
        self,
        chat_id: int,
        opened_at: datetime | None,
    ) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        state.question_opened_at = opened_at
        await self.save_room_state(chat_id, state)
        return state

    async def set_deadline(
        self,
        chat_id: int,
        deadline: datetime | None,
    ) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        state.deadline = deadline
        await self.save_room_state(chat_id, state)
        return state

    async def set_answer_button_enabled(
        self,
        chat_id: int,
        enabled: bool,
    ) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        state.button_enable = enabled
        await self.save_room_state(chat_id, state)
        return state

    async def set_answer_owner(
        self,
        chat_id: int,
        tg_id: int | None,
    ) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        state.user_id_answer = tg_id
        await self.save_room_state(chat_id, state)
        return state

    async def reset_answered_users(self, chat_id: int) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        state.answered_users_ids = []
        await self.save_room_state(chat_id, state)
        return state

    async def add_answered_user(self, chat_id: int, tg_id: int) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        if tg_id not in state.answered_users_ids:
            state.answered_users_ids.append(tg_id)

        await self.save_room_state(chat_id, state)
        return state

    async def prepare_room_for_game(
        self,
        chat_id: int,
        theme_id: int,
        question_ids: list[int],
        message_id: int | None = None,
    ) -> RoomState | None:
        state = await self.get_room_state(chat_id)
        if state is None:
            return None

        state.theme_id = theme_id
        state.question_ids = question_ids
        state.current_question_id = None
        state.question_opened_at = None
        state.answered_users_ids = []
        state.user_id_answer = None
        state.button_enable = False
        state.deadline = None

        if message_id is not None:
            state.message_id = message_id

        for player in state.players:
            player.confirmed = False
            player.score = 0

        await self.save_room_state(chat_id, state)
        return state
