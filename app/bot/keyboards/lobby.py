from app.aiotg.types.keyboard import InlineKeyboardButton, InlineKeyboardMarkup


def lobby_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='➕ Войти', callback_data='lobby:join'),
                InlineKeyboardButton(text='➖ Выйти', callback_data='lobby:leave'),
            ],
            [
                InlineKeyboardButton(
                    text='✅ Подтвердить сбор',
                    callback_data='lobby:approve',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='☑️ Подтвердить участие',
                    callback_data='lobby:confirm',
                ),
            ],
        ]
    )


def question_buzz_kb(enabled: bool = True) -> InlineKeyboardMarkup:
    text = '🎯 Ответить' if enabled else '⏳ Идёт ответ'
    data = 'game:buzz' if enabled else 'game:noop'

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=text, callback_data=data),
            ],
        ]
    )


def answers_kb(question_id: int, answers: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for answer_id, title in answers:
        rows.append(
            [
                InlineKeyboardButton(
                    text=title,
                    callback_data=f'game:answer:{question_id}:{answer_id}',
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=rows)


def results_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='📊 Таблица', callback_data='game:results'),
            ],
        ]
    )
