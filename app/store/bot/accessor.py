import typing

from app.aiotg.client.bot import Bot
from app.base.base_accessor import BaseAccessor
from app.bot.bot import dp as bot_dispatcher

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotAccessor(BaseAccessor):
    def __init__(self, app: 'Application'):
        super().__init__(app)

        self.app = app

    async def connect(self, app: 'Application'):
        await self.start_bot()

    async def start_bot(self):
        async with Bot(self.app.config.bot.token) as bot:
            await bot_dispatcher.start_polling(bot)
