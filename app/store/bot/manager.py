import typing
from logging import getLogger

from app.store.bot.api import BotApi
from app.store.bot.poller import Poller
from app.store.bot.router import Router
from app.store.bot.schemas import UpdateList

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: 'Application'):
        self.app = app
        self.api = BotApi(self.app.config.bot.token)
        self.logger = getLogger('bot_manager')
        self.poller: Poller | None = None
        self.router: Router | None = None

    async def connect(self):
        if self.router is None:
            raise RuntimeError('Router is not setup')

        await self.api.connect()
        await self.poller_start()

    async def disconnect(self):
        if self.poller:
            await self.poller.stop()

        await self.api.disconnect()

    def setup_router(self, router: Router) -> None:
        self.router = router

    async def poller_start(self):
        if self.poller is None:
            self.poller = Poller(self.app.store)
        self.logger.info('start polling')
        self.poller.start()

    async def poll(self) -> None:
        data = await self.api.get_updates()
        is_ok = data.get('ok', False)
        if not is_ok:
            self.logger.error(data)
            raise RuntimeError('Telegram API returned an error')

        updates = UpdateList.model_validate(data)

        self.logger.debug(updates)

        if not updates.result:
            return

        self.api.offset = updates.result[-1].update_id + 1

        await self.handle_updates(updates)

    async def handle_updates(self, updates: UpdateList):
        for update in updates.result:
            await self.router.dispatch(update)
