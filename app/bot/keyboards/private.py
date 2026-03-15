from app.aiotg.types.keyboard import KeyboardButton, ReplyKeyboardMarkup


def private_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='/help'),
                KeyboardButton(text='/about'),
            ],
            [
                KeyboardButton(text='/play'),
            ],
        ],
        resize_keyboard=True,
    )
