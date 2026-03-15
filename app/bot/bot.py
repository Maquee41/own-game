import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

from app.aiotg.client.bot import Bot
from app.aiotg.dispatcher.dispatcher import Dispatcher
from app.aiotg.methods.answer_callback_query import answer_callback_query
from app.aiotg.methods.edit_message import edit_message
from app.aiotg.methods.send_message import send_message
from app.aiotg.types.update import Update
from app.bot.keyboards.lobby import answers_kb, lobby_kb, question_buzz_kb
from app.bot.keyboards.private import private_menu_kb
from app.game.models import RoomStatus
from app.game.schemas import Player, RoomState

dp = Dispatcher()

MAX_PLAYERS = 3
APPROVE_TIMEOUT = 20
QUESTION_TIMEOUT = 15
QUESTIONS_PER_GAME = 5

APPROVE_TASKS: dict[int, asyncio.Task] = {}
QUESTION_TASKS: dict[int, asyncio.Task] = {}
GAME_START_TS: dict[int, datetime] = {}


def utcnow() -> datetime:
    return datetime.now(UTC)


def cancel_task(tasks: dict[int, asyncio.Task], chat_id: int) -> None:
    task = tasks.pop(chat_id, None)
    if task and not task.done():
        task.cancel()


async def get_user_display_name(store: Any, tg_id: int) -> str:
    user = await store.game.get_user_by_tg(tg_id)
    if user is None:
        return str(tg_id)
    if user.username:
        return f'@{user.username}'
    return f'user_{tg_id}'


async def render_players_block(store: Any, state: RoomState) -> str:
    lines: list[str] = []
    for idx, player in enumerate(state.players, start=1):
        name = await get_user_display_name(store, player.tg_id)
        mark = '✅' if player.confirmed else '⏳'
        lines.append(f'{idx}️⃣ {name} {mark}')
    while len(lines) < MAX_PLAYERS:
        lines.append(f'{len(lines)+1}️⃣ -')
    return '\n'.join(lines)


async def render_lobby_text(store: Any, state: RoomState) -> str:
    players_block = await render_players_block(store, state)
    return (
        '🎮 Своя игра\n\n'
        'Лобби:\n'
        f'{players_block}\n\n'
        f'Игроков: {len(state.players)}/{MAX_PLAYERS}\n'
        'Нажмите «Войти», чтобы занять слот.\n'
        'Когда игроков станет 3, запустите подтверждение.'
    )


async def render_confirm_text(store: Any, state: RoomState) -> str:
    players_block = await render_players_block(store, state)
    confirmed_count = sum(1 for p in state.players if p.confirmed)
    return (
        '🎮 Своя игра\n\n'
        'Подтверждение участия:\n'
        f'{players_block}\n\n'
        f'Подтвердили: {confirmed_count}/{MAX_PLAYERS}\n'
        f'У вас {APPROVE_TIMEOUT} секунд.'
    )


async def render_results_text(store: Any, state: RoomState) -> str:
    players = sorted(state.players, key=lambda p: p.score, reverse=True)
    lines = ['🏁 Результаты игры', '']
    for idx, player in enumerate(players, start=1):
        name = await get_user_display_name(store, player.tg_id)
        lines.append(f'{idx}. {name} — {player.score}')
    return '\n'.join(lines)


async def render_question_text(
    store: Any,
    state: RoomState,
    question_title: str,
    question_no: int,
    total_questions: int,
    owner_tg_id: int | None = None,
) -> str:
    scoreboard = []
    for player in sorted(state.players, key=lambda p: p.score, reverse=True):
        name = await get_user_display_name(store, player.tg_id)
        scoreboard.append(f'• {name}: {player.score}')

    owner_line = ''
    if owner_tg_id is not None:
        owner_line = f'\n\nОтвечает: {await get_user_display_name(store, owner_tg_id)}'

    return (
        f'❓ Вопрос {question_no}/{total_questions}\n\n'
        f'{question_title}\n'
        f'{owner_line}\n\n'
        'Счёт:\n'
        + '\n'.join(scoreboard)
    ).strip()


async def ensure_tg_user(store: Any, tg_user: Any) -> None:
    await store.game.get_or_create_user(
        tg_id=tg_user.id_,
        username=tg_user.username,
    )


async def get_room_or_alert(
    bot: Bot,
    store: Any,
    update: Update,
):
    cq = update.callback_query
    if cq is None or cq.message is None:
        return None, None

    room = await store.game.get_room_by_chat_id(cq.message.chat.id_)
    if room is None:
        await answer_callback_query(
            bot=bot,
            callback_query_id=cq.id,
            text='Активной комнаты нет',
            show_alert=True,
        )
        return None, None

    state = await store.game.get_room_state(cq.message.chat.id_)
    if state is None:
        await answer_callback_query(
            bot=bot,
            callback_query_id=cq.id,
            text='Состояние комнаты не найдено',
            show_alert=True,
        )
        return None, None

    return room, state


async def show_lobby(bot: Bot, store: Any, chat_id: int) -> None:
    state = await store.game.get_room_state(chat_id)
    if state is None or state.message_id is None:
        return

    await edit_message(
        bot=bot,
        chat_id=chat_id,
        message_id=state.message_id,
        text=await render_lobby_text(store, state),
        reply_markup=lobby_kb(),
    )


async def show_confirm(bot: Bot, store: Any, chat_id: int) -> None:
    state = await store.game.get_room_state(chat_id)
    if state is None or state.message_id is None:
        return

    await edit_message(
        bot=bot,
        chat_id=chat_id,
        message_id=state.message_id,
        text=await render_confirm_text(store, state),
        reply_markup=lobby_kb(),
    )


async def finish_game(bot: Bot, store: Any, chat_id: int) -> None:
    room = await store.game.get_room_by_chat_id(chat_id)
    state = await store.game.get_room_state(chat_id)
    if room is None or state is None or state.message_id is None:
        return

    cancel_task(QUESTION_TASKS, chat_id)
    cancel_task(APPROVE_TASKS, chat_id)

    await store.game.update_room_status(chat_id, RoomStatus.FINISHED)

    for player in state.players:
        await store.game.update_user_score(player.tg_id, player.score)

    text = await render_results_text(store, state)

    await edit_message(
        bot=bot,
        chat_id=chat_id,
        message_id=state.message_id,
        text=text,
        reply_markup=None,
    )

    await store.game.delete_room(chat_id)


async def start_next_question(bot: Bot, store: Any, chat_id: int) -> None:
    state = await store.game.get_room_state(chat_id)
    if state is None or state.message_id is None:
        return

    cancel_task(QUESTION_TASKS, chat_id)

    if not state.question_ids:
        await finish_game(bot, store, chat_id)
        return

    question_id = state.question_ids[0]
    state.question_ids = state.question_ids[1:]
    state.current_question_id = question_id
    state.question_opened_at = utcnow()
    state.deadline = utcnow() + timedelta(seconds=QUESTION_TIMEOUT)
    state.answered_users_ids = []
    state.user_id_answer = None
    state.button_enable = True
    await store.game.save_room_state(chat_id, state)

    question = await store.game.get_question_by_id(question_id)
    if question is None:
        await finish_game(bot, store, chat_id)
        return

    asked_count = QUESTIONS_PER_GAME - len(state.question_ids)
    text = await render_question_text(
        store=store,
        state=state,
        question_title=question.title,
        question_no=asked_count,
        total_questions=QUESTIONS_PER_GAME,
    )

    await edit_message(
        bot=bot,
        chat_id=chat_id,
        message_id=state.message_id,
        text=text,
        reply_markup=question_buzz_kb(enabled=True),
    )

    QUESTION_TASKS[chat_id] = asyncio.create_task(
        question_timeout_worker(bot, store, chat_id, question_id)
    )


async def start_match(bot: Bot, store: Any, chat_id: int) -> None:
    room = await store.game.get_room_by_chat_id(chat_id)
    state = await store.game.get_room_state(chat_id)
    if room is None or state is None or state.message_id is None:
        return

    themes = await store.game.list_themes()
    if not themes:
        await edit_message(
            bot=bot,
            chat_id=chat_id,
            message_id=state.message_id,
            text='Нет тем в базе. Сначала добавь темы и вопросы.',
            reply_markup=None,
        )
        return

    theme = themes[0]
    questions = await store.game.get_random_questions(theme.id, QUESTIONS_PER_GAME)
    if len(questions) < QUESTIONS_PER_GAME:
        await edit_message(
            bot=bot,
            chat_id=chat_id,
            message_id=state.message_id,
            text='Недостаточно вопросов в теме для игры.',
            reply_markup=None,
        )
        return

    GAME_START_TS[chat_id] = utcnow()

    await store.game.update_room_status(chat_id, RoomStatus.IN_ROUND)

    state.theme_id = theme.id
    state.current_question_id = None
    state.question_ids = [q.id for q in questions]
    state.answered_users_ids = []
    state.user_id_answer = None
    state.button_enable = False
    state.deadline = None
    state.question_opened_at = None
    for player in state.players:
        player.score = 0

    await store.game.save_room_state(chat_id, state)

    await start_next_question(bot, store, chat_id)


async def approve_timeout_worker(bot: Bot, store: Any, chat_id: int) -> None:
    try:
        await asyncio.sleep(APPROVE_TIMEOUT)
    except asyncio.CancelledError:
        return

    state = await store.game.get_room_state(chat_id)
    if state is None or state.message_id is None:
        return

    all_confirmed = len(state.players) == MAX_PLAYERS and all(p.confirmed for p in state.players)
    if all_confirmed:
        await start_match(bot, store, chat_id)
        return

    for player in state.players:
        player.confirmed = False

    await store.game.save_room_state(chat_id, state)

    await edit_message(
        bot=bot,
        chat_id=chat_id,
        message_id=state.message_id,
        text='⌛ Не все подтвердили участие за 20 секунд.\n\n'
        + await render_lobby_text(store, state),
        reply_markup=lobby_kb(),
    )


async def question_timeout_worker(
    bot: Bot,
    store: Any,
    chat_id: int,
    question_id: int,
) -> None:
    try:
        await asyncio.sleep(QUESTION_TIMEOUT)
    except asyncio.CancelledError:
        return

    state = await store.game.get_room_state(chat_id)
    if state is None or state.message_id is None:
        return

    if state.current_question_id != question_id:
        return

    question = await store.game.get_question_by_id(question_id)
    if question is None:
        await finish_game(bot, store, chat_id)
        return

    correct = next((a.title for a in question.answers if a.is_correct), '—')

    state.button_enable = False
    state.user_id_answer = None
    await store.game.save_room_state(chat_id, state)

    await edit_message(
        bot=bot,
        chat_id=chat_id,
        message_id=state.message_id,
        text=(
            f'⌛ Время на вопрос вышло.\n\n'
            f'Правильный ответ: {correct}\n\n'
            + await render_results_text(store, state)
        ),
        reply_markup=None,
    )

    await asyncio.sleep(2)
    await start_next_question(bot, store, chat_id)


@dp.command('start', chat_types={'private'})
async def start(bot: Bot, store: Any, update: Update):
    await ensure_tg_user(store, update.message.from_user)

    await send_message(
        bot=bot,
        chat_id=update.message.from_user.id_,
        text=(
            'Привет! Я бот для игры «Своя игра».\n\n'
            'Что умею:\n'
            '• создаю лобби в группе\n'
            '• собираю 3 игроков\n'
            '• подтверждаю участие\n'
            '• провожу раунд с вопросами и ответами\n\n'
            'Добавь меня в группу и используй /start_game'
        ),
        reply_markup=private_menu_kb(),
    )


@dp.command('help', chat_types={'private'})
async def help_cmd(bot: Bot, store: Any, update: Update):
    await send_message(
        bot=bot,
        chat_id=update.message.from_user.id_,
        text=(
            'В группе используй /start_game.\n'
            'Дальше:\n'
            '1. Игроки нажимают «Войти»\n'
            '2. Когда вас трое — «Подтвердить сбор»\n'
            '3. Все жмут «Подтвердить участие»\n'
            '4. Начинается игра'
        ),
        reply_markup=private_menu_kb(),
    )


@dp.command('about', chat_types={'private'})
async def about_cmd(bot: Bot, store: Any, update: Update):
    await send_message(
        bot=bot,
        chat_id=update.message.from_user.id_,
        text='MVP-версия «Своей игры» на чистом Telegram Bot API.',
        reply_markup=private_menu_kb(),
    )


@dp.command('play', chat_types={'private'})
async def play_cmd(bot: Bot, store: Any, update: Update):
    await send_message(
        bot=bot,
        chat_id=update.message.from_user.id_,
        text='Чтобы начать, добавь меня в группу и отправь /start_game.',
        reply_markup=private_menu_kb(),
    )


@dp.command('start_game', chat_types={'group', 'supergroup'})
async def start_game(bot: Bot, store: Any, update: Update):
    chat_id = update.message.chat.id_
    tg_user = update.message.from_user

    await ensure_tg_user(store, tg_user)

    existing_room = await store.game.get_room_by_chat_id(chat_id)
    existing_state = await store.game.get_room_state(chat_id) if existing_room else None

    if existing_room is not None and existing_state is not None:
        try:
            if existing_state.message_id is not None:
                await edit_message(
                    bot=bot,
                    chat_id=chat_id,
                    message_id=existing_state.message_id,
                    text=await render_lobby_text(store, existing_state),
                    reply_markup=lobby_kb(),
                )
                return
        except Exception:
            pass

        sent = await send_message(
            bot=bot,
            chat_id=chat_id,
            text=await render_lobby_text(store, existing_state),
            reply_markup=lobby_kb(),
        )

        existing_state.message_id = sent.id_
        await store.game.save_room_state(chat_id, existing_state)
        return

    initial_state = RoomState(
        players=[
            Player(
                tg_id=tg_user.id_,
                confirmed=False,
                score=0,
            )
        ],
        question_ids=[],
        answered_users_ids=[],
        button_enable=False,
    )

    sent = await send_message(
        bot=bot,
        chat_id=chat_id,
        text='Создаю лобби...',
        reply_markup=lobby_kb(),
    )

    initial_state.message_id = sent.id_

    await store.game.create_room(
        chat_id=chat_id,
        status=RoomStatus.LOBBY,
        state=initial_state.model_dump(mode='json'),
    )

    await edit_message(
        bot=bot,
        chat_id=chat_id,
        message_id=sent.id_,
        text=await render_lobby_text(store, initial_state),
        reply_markup=lobby_kb(),
    )


@dp.callback('lobby:', chat_types={'group', 'supergroup'})
async def lobby_callbacks(bot: Bot, store: Any, update: Update):
    cq = update.callback_query
    if cq is None or cq.message is None or cq.data is None:
        return

    room, state = await get_room_or_alert(bot, store, update)
    if room is None or state is None:
        return

    chat_id = cq.message.chat.id_
    tg_user = cq.from_user
    action = cq.data.split(':', 1)[1]

    await ensure_tg_user(store, tg_user)

    if action == 'join':
        if len(state.players) >= MAX_PLAYERS:
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Лобби уже заполнено',
                show_alert=True,
            )
            return

        if any(p.tg_id == tg_user.id_ for p in state.players):
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Ты уже в лобби',
            )
            return

        state.players.append(
            Player(
                tg_id=tg_user.id_,
                confirmed=False,
                score=0,
            )
        )
        await store.game.save_room_state(chat_id, state)

        await answer_callback_query(
            bot=bot,
            callback_query_id=cq.id,
            text='Ты вошёл в лобби',
        )
        await show_lobby(bot, store, chat_id)
        return

    if action == 'leave':
        if tg_user.id_ == state.players[0].tg_id:
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Создатель не может выйти. Пересоздай игру.',
                show_alert=True,
            )
            return

        if not any(p.tg_id == tg_user.id_ for p in state.players):
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Тебя нет в лобби',
            )
            return

        state.players = [p for p in state.players if p.tg_id != tg_user.id_]
        await store.game.save_room_state(chat_id, state)

        await answer_callback_query(
            bot=bot,
            callback_query_id=cq.id,
            text='Ты вышел из лобби',
        )
        await show_lobby(bot, store, chat_id)
        return

    if action == 'approve':
        if len(state.players) != MAX_PLAYERS:
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Нужно 3 игрока',
                show_alert=True,
            )
            return

        for player in state.players:
            player.confirmed = False
        await store.game.save_room_state(chat_id, state)

        cancel_task(APPROVE_TASKS, chat_id)
        APPROVE_TASKS[chat_id] = asyncio.create_task(
            approve_timeout_worker(bot, store, chat_id)
        )

        await answer_callback_query(
            bot=bot,
            callback_query_id=cq.id,
            text='Запущено подтверждение участия',
        )
        await show_confirm(bot, store, chat_id)
        return

    if action == 'confirm':
        player = next((p for p in state.players if p.tg_id == tg_user.id_), None)
        if player is None:
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Ты не в лобби',
                show_alert=True,
            )
            return

        if player.confirmed:
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Ты уже подтвердил участие',
            )
            return

        player.confirmed = True
        await store.game.save_room_state(chat_id, state)

        await answer_callback_query(
            bot=bot,
            callback_query_id=cq.id,
            text='Участие подтверждено',
        )
        await show_confirm(bot, store, chat_id)

        if len(state.players) == MAX_PLAYERS and all(p.confirmed for p in state.players):
            cancel_task(APPROVE_TASKS, chat_id)
            await start_match(bot, store, chat_id)
        return


@dp.callback('game:', chat_types={'group', 'supergroup'})
async def game_callbacks(bot: Bot, store: Any, update: Update):
    cq = update.callback_query
    if cq is None or cq.message is None or cq.data is None:
        return

    room, state = await get_room_or_alert(bot, store, update)
    if room is None or state is None:
        return

    chat_id = cq.message.chat.id_
    parts = cq.data.split(':')
    action = parts[1]

    if action == 'noop':
        await answer_callback_query(
            bot=bot,
            callback_query_id=cq.id,
            text='Сейчас отвечает другой игрок',
        )
        return

    if action == 'results':
        await answer_callback_query(
            bot=bot,
            callback_query_id=cq.id,
            text='Таблица обновлена',
        )
        await edit_message(
            bot=bot,
            chat_id=chat_id,
            message_id=state.message_id,
            text=await render_results_text(store, state),
            reply_markup=None,
        )
        return

    if action == 'buzz':
        if state.current_question_id is None:
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Сейчас нет активного вопроса',
                show_alert=True,
            )
            return

        if not state.button_enable:
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Кнопка уже занята',
            )
            return

        if not any(p.tg_id == cq.from_user.id_ for p in state.players):
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Ты не участник игры',
                show_alert=True,
            )
            return

        if cq.from_user.id_ in state.answered_users_ids:
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Ты уже отвечал на этот вопрос',
            )
            return

        question = await store.game.get_question_by_id(state.current_question_id)
        if question is None:
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Вопрос не найден',
                show_alert=True,
            )
            return

        state.button_enable = False
        state.user_id_answer = cq.from_user.id_
        await store.game.save_room_state(chat_id, state)

        answers = [(a.id, a.title) for a in question.answers]

        asked_count = QUESTIONS_PER_GAME - len(state.question_ids)
        text = await render_question_text(
            store=store,
            state=state,
            question_title=question.title,
            question_no=asked_count,
            total_questions=QUESTIONS_PER_GAME,
            owner_tg_id=cq.from_user.id_,
        )

        await answer_callback_query(
            bot=bot,
            callback_query_id=cq.id,
            text='Ты первый на кнопке',
        )

        await edit_message(
            bot=bot,
            chat_id=chat_id,
            message_id=state.message_id,
            text=text,
            reply_markup=answers_kb(question.id, answers),
        )
        return

    if action == 'answer':
        if len(parts) != 4:
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Некорректные данные ответа',
                show_alert=True,
            )
            return

        question_id = int(parts[2])
        answer_id = int(parts[3])

        if state.current_question_id != question_id:
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Этот вопрос уже завершён',
            )
            return

        if state.user_id_answer != cq.from_user.id_:
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Сейчас отвечает другой игрок',
                show_alert=True,
            )
            return

        question = await store.game.get_question_by_id(question_id)
        if question is None:
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Вопрос не найден',
                show_alert=True,
            )
            return

        selected = next((a for a in question.answers if a.id == answer_id), None)
        correct = next((a for a in question.answers if a.is_correct), None)

        if selected is None or correct is None:
            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Ответ не найден',
                show_alert=True,
            )
            return

        if selected.is_correct:
            for player in state.players:
                if player.tg_id == cq.from_user.id_:
                    player.score += 1
                    break

            state.button_enable = False
            state.user_id_answer = None
            await store.game.save_room_state(chat_id, state)

            await answer_callback_query(
                bot=bot,
                callback_query_id=cq.id,
                text='Верно!',
            )

            await edit_message(
                bot=bot,
                chat_id=chat_id,
                message_id=state.message_id,
                text=(
                    f'✅ Верный ответ: {correct.title}\n\n'
                    + await render_results_text(store, state)
                ),
                reply_markup=None,
            )

            await asyncio.sleep(2)
            await start_next_question(bot, store, chat_id)
            return

        if cq.from_user.id_ not in state.answered_users_ids:
            state.answered_users_ids.append(cq.from_user.id_)

        state.user_id_answer = None

        remaining = [
            p for p in state.players
            if p.tg_id not in state.answered_users_ids
        ]

        await answer_callback_query(
            bot=bot,
            callback_query_id=cq.id,
            text='Неверно',
        )

        if not remaining:
            state.button_enable = False
            await store.game.save_room_state(chat_id, state)

            await edit_message(
                bot=bot,
                chat_id=chat_id,
                message_id=state.message_id,
                text=(
                    f'❌ Все ошиблись.\n'
                    f'Правильный ответ: {correct.title}\n\n'
                    + await render_results_text(store, state)
                ),
                reply_markup=None,
            )

            await asyncio.sleep(2)
            await start_next_question(bot, store, chat_id)
            return

        state.button_enable = True
        await store.game.save_room_state(chat_id, state)

        asked_count = QUESTIONS_PER_GAME - len(state.question_ids)
        text = await render_question_text(
            store=store,
            state=state,
            question_title=question.title,
            question_no=asked_count,
            total_questions=QUESTIONS_PER_GAME,
        )

        await edit_message(
            bot=bot,
            chat_id=chat_id,
            message_id=state.message_id,
            text=text + '\n\n❌ Неверно. Остальные могут нажать кнопку.',
            reply_markup=question_buzz_kb(enabled=True),
        )
