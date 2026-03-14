from app.aiotg.types.keyboard import InlineKeyboardButton, InlineKeyboardMarkup


def init_kb() -> dict:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Войти', callback_data='init:enter'),
                InlineKeyboardButton(text='Выйти', callback_data='init:exit'),
            ]
        ]
    )

    return kb.model_dump()
