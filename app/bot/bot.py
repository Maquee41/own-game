from app.aiotg.client.bot import Bot
from app.aiotg.dispatcher.dispatcher import Dispatcher
from app.aiotg.methods.send_message import send_message
from app.aiotg.types.update import Update

dp = Dispatcher()


@dp.command('start', chat_types={'private'})
async def start(bot: Bot, update: Update):
    await send_message(
        bot=bot,
        chat_id=update.message.chat.id_,
        text='Привет! Я игровой бот.\n'
        'В личных сообщениях я рассказываю о себе и правилах.\n'
        'Чтобы играть, добавь меня в группу.\n\n'
        'Команды:\n'
        '/help — помощь\n'
        '/about — о боте\n'
        '/play — как начать игру в группе\n\n',
    )
