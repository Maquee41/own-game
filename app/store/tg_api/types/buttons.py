class KeyboardButton:
    def __init__(self, text: str):
        self.text = text


class InlineKeyboardButton:
    def __init__(self, callback_data: str, text: str):
        self.text = text
        self.callback_data = callback_data


class InlineKeyboard:
    def __init__(self, buttons: list[InlineKeyboardButton]):
        self.buttons: list[InlineKeyboardButton] = buttons
