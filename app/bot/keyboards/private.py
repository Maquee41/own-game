from app.aiotg.types.keyboard import KeyboardButton, ReplyKeyboardMarkup


def start_nav() -> dict:
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Помощь'),
                KeyboardButton(text='О боте'),
            ],
            [
                KeyboardButton(text='Как играть?'),
            ],
        ]
    )

    return kb.model_dump()
