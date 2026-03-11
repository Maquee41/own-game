import typing
from logging import getLogger

from aiohttp import ClientSession, TCPConnector

from app.store.bot.api import BotApi
from app.store.bot.poller import Poller
from app.store.bot.router import Router
from app.store.bot.schemes import UpdateList

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_HOST = 'https://api.telegram.org'


class BotManager:
    def __init__(self, app: 'Application'):
        self.app = app
        self.api = BotApi(self.app.config.bot.token)
        self.bot = None
        self.logger = getLogger('handler')
        self.offset: int | None = None
        self.poller: Poller | None = None
        self.router: Router | None = None
        self.session: ClientSession | None = None

    async def connect(self):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        await self.poller_start()

    async def disconnect(self):
        if self.session:
            await self.session.close()

    async def setup_router(self, router: Router) -> None:
        self.router = router

    async def poller_start(self):
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

        if len(updates.result) == 0:
            self.offset = -1
        else:
            self.offset = updates.result[-1].update_id + 1

        await self.handle_updates(updates)

    async def handle_updates(self, updates: UpdateList):
        for update in updates.result:
            await self.router.dispatch(update)
