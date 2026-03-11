from urllib.parse import urlencode

from aiohttp import ClientSession

API_HOST = 'https://api.telegram.org'


class BotApi:
    def __init__(self, token: str, limit: int = 50, timeout: int = 30):
        self.allowed_updates = ['message', 'callback_query']
        self.limit: int = limit
        self.offset: int = -1
        self.session: ClientSession | None = None
        self.token: str = token
        self.timeout: int = timeout

    def _check_session(self) -> ClientSession:
        if self.session is None:
            raise RuntimeError('BotApi session is not initialized')
        return self.session

    async def _request(
        self,
        method: str,
        http_method: str = 'GET',
        params: dict | None = None,
        json: dict | None = None,
    ) -> dict:
        session = self._check_session()
        url = f'{API_HOST}/bot{self.token}/{method}'

        if params:
            url += f'?{urlencode(params)}'

        async with session.request(http_method, url, json=json) as response:
            response.raise_for_status()
            data = await response.json()

            if not data.get('ok'):
                raise RuntimeError('Telegram API returned error')

            return data

    async def connect(self) -> None:
        self.session = ClientSession()

    async def disconnect(self) -> None:
        if self.session:
            await self.session.close()

        self.session = None

    async def get_me(self) -> dict:
        session = self._check_session()
        async with session.get() as response:
            response.raise_for_status()
            data = await response.json()
            return data

    async def send_message(self, chat_id: int, text: str) -> dict:
        return await self._request(
            method='sendMessage',
            http_method='POST',
            json={
                'chat_id': chat_id,
                'text': text,
            },
        )

    async def get_updates(self) -> dict:
        return await self._request(
            method='getUpdates',
            params={
                'allowed_updates': self.allowed_updates,
                'offset': self.offset,
                'limit': self.limit,
                'timeout': self.timeout,
            },
        )
