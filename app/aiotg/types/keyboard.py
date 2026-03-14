from pydantic import BaseModel


class InlineKeyboardButton(BaseModel):
    text: str
    callback_data: str | None = None


class InlineKeyboardMarkup(BaseModel):
    inline_keyboard: list[list[InlineKeyboardButton]]


class KeyboardButton(BaseModel):
    text: str


class ReplyKeyboardMarkup(BaseModel):
    keyboard: list[list[KeyboardButton]]
    resize_keyboard: bool = True
    one_time_keyboard: bool = False
    selective: bool = False
