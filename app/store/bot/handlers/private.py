from app.store.bot.router import Router
from app.store.bot.schemas import Update


def register_private_handlers(router: Router) -> None:
    @router.command('/start', chat_type='private')
    async def cmd_start(update: Update):
        message = update.message
        text = (
            'Привет! Я игровой бот.\n\n'
            'В личных сообщениях я рассказываю о себе и правилах.\n'
            'Чтобы играть, добавь меня в группу.\n\n'
            'Команды:\n'
            '/help — помощь\n'
            '/about — о боте\n'
            '/play — как начать игру в группе'
        )
        await router.app.store.bot.manager.api.send_message(
            chat_id=message.chat.id_, text=text
        )

    @router.command('/help', chat_type='private')
    async def cmd_help(update: Update): ...

    @router.command('/about', chat_type='private')
    async def cmd_about(update: Update): ...

    @router.command('/play', chat_type='private')
    async def cmd_play(update: Update): ...
