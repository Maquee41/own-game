import typing
from urllib.parse import urlencode

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.tg_api.dataclasses import Chat, Message, Update, User
from app.store.tg_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_HOST = 'https://api.telegram.org'

GREETING = 'Hi!'


class TelegramApiAccessor(BaseAccessor):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        self.is_checked: bool = False
        self.offset: int | None = None
        self.session: ClientSession | None = None
        self.poller: Poller | None = None
        self.token: str = self.app.config.bot.token

    async def connect(self, app: 'Application') -> None:
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))

        self.poller = Poller(app.store)
        self.logger.info('start polling')
        self.poller.start()

    async def disconnect(self, app: 'Application'):
        if self.session:
            await self.session.close()

    def _build_query(self, method: str, params: dict) -> str:
        return f'{API_HOST}/bot{self.token}/{method}?{urlencode(params)}'

    async def poll(
        self,
        # TODO: get only necessery updates
        # allowed_updates: list,
        limit: int = 100,
        timeout: int = 30,
    ) -> None:
        async with self.session.get(
            self._build_query(
                method='getUpdates',
                params={
                    'offset': self.offset,
                    'limit': limit,
                    'timeout': timeout,
                    # TODO: get only necessery updates configuring "allowed_updates"
                },
            )
        ) as response:
            data = await response.json()

            is_ok = data.get('ok', False)
            if not is_ok:
                self.logger.error(data)
                raise RuntimeError('Telegram API returned an error')

            self.logger.info(data)

            updates = [
                Update(
                    update_id=update['update_id'],
                    message=Message(
                        chat=Chat(
                            id_=update['message']['chat']['id'],
                        ),
                        from_=User(
                            id_=update['message']['from']['id'],
                            username=update['message']['from']['username'],
                            first_name=update['message']['from']['first_name'],
                            is_bot=update['message']['from']['is_bot'],
                            language_code=update['message']['from']['language_code'],
                        ),
                        text=update['message']['text'],
                    ),
                )
                for update in data.get('result', [])
            ]

            if len(data.get('result', [])) == 0:
                self.offset = -1
            else:
                self.offset = data['result'][-1]['update_id'] + 1
            await self.app.store.bot_manager.handle_updates(updates)

    async def get_me(self) -> None:
        async with self.session.get(
            self._build_query(
                method='getMe',
                params={},
            )
        ) as response:
            data = await response.json()
            self.logger.info(data)

    async def greeting(self, user_id: int) -> None:
        async with self.session.post(
            self._build_query(
                method='sendMessage',
                params={
                    'chat_id': user_id,
                    'text': GREETING,
                },
            )
        ) as response:
            data = await response.json()
            self.logger.info(data)
