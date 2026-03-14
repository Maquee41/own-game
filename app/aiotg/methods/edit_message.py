from app.aiotg.client.bot import Bot
from app.aiotg.types.message import Message


async def edit_message(
    bot: Bot,
    chat_id: int,
    message_id: int,
    text: str,
    reply_markup: dict | None = None,
) -> Message | bool:
    data = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
    }

    if reply_markup is not None:
        data['reply_markup'] = reply_markup

    return await bot.request(
        'editMessageText',
        data=data,
        response_model=Message,
    )
