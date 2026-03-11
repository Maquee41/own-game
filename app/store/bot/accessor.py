import typing

from app.base.base_accessor import BaseAccessor
from app.store.bot.manager import BotManager
from app.store.bot.routes import setup_router

if typing.TYPE_CHECKING:
    from app.web.app import Application


class TelegramApiAccessor(BaseAccessor):
    def __init__(self, app: 'Application'):
        super().__init__(app)

        self.manager: BotManager = BotManager(app)
        self.manager.setup_router(setup_router(app))

    async def connect(self, app: 'Application') -> None:
        await self.manager.connect()

    async def disconnect(self, app: 'Application'):
        await self.manager.disconnect()
