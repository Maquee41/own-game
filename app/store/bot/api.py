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

    def _build_query(self, method: str, params: dict) -> str:
        return f'{API_HOST}/bot{self.token}/{method}?{urlencode(params)}'

    async def get_me(self) -> dict:
        async with self.session.get(
            self._build_query(
                method='getMe',
                params={},
            )
        ) as response:
            data = await response.json()
            return data

    async def send_message(self, chat_id: int, text: str) -> dict:
        async with self.session.post(
            self._build_query(
                method='sendMessage',
                params={
                    'chat_id': chat_id,
                    'text': text,
                },
            )
        ) as response:
            data = await response.json()
            return data

    async def get_updates(self) -> dict:
        async with self.session.get(
            self._build_query(
                method='getUpdates',
                params={
                    'allowed_updates': self.allowed_updates,
                    'offset': self.offset,
                    'limit': self.limit,
                    'timeout': self.timeout,
                },
            )
        ) as response:
            data = await response.json()
            return data
