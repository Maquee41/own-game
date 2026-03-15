from app.aiotg.client.bot import Bot
from app.aiotg.types.keyboard import InlineKeyboardMarkup, ReplyKeyboardMarkup
from app.aiotg.types.message import Message


async def send_message(
    bot: Bot,
    chat_id: int,
    text: str,
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None,
) -> Message:
    data = {
        'chat_id': chat_id,
        'text': text,
    }
    if reply_markup is not None:
        data['reply_markup'] = reply_markup.model_dump()

    return await bot.request('sendMessage', data=data, response_model=Message)
