import typing

from app.base.base_accessor import BaseAccessor
from app.store.bot.manager import BotManager

if typing.TYPE_CHECKING:
    from app.web.app import Application


class TelegramApiAccessor(BaseAccessor):
    def __init__(self, app: 'Application'):
        super().__init__(app)

        self.bot_manager: BotManager = BotManager(app)

    async def connect(self, app: 'Application') -> None:
        await self.bot_manager.connect()

    async def disconnect(self, app: 'Application'):
        await self.bot_manager.disconnect()
