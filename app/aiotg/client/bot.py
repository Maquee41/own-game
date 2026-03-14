from logging import getLogger
from typing import Any, Literal, TypeVar

from aiohttp import ClientSession
from pydantic import BaseModel

from app.aiotg.types.user import User

API_URL = 'https://api.telegram.org'

T = TypeVar('T', bound=BaseModel)


class TelegramAPIError(Exception):
    pass


class Bot:
    def __init__(self, token: str, session: ClientSession | None = None):
        self.token = token
        self._external_session = session is not None
        self.logger = getLogger('bot')
        self.session = session
        self._me: User | None = None

    async def __aenter__(self) -> 'Bot':
        if self.session is None:
            self.session = ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.session and not self._external_session:
            await self.session.close()

    async def request(
        self,
        method: str,
        data: dict[str, Any] | None = None,
        response_model: type[T] | None = None,
        http_method: Literal['GET', 'POST'] = 'POST',
    ) -> T | list[Any] | dict[str, Any] | bool:
        if self.session is None:
            raise RuntimeError('Bot session is not initialized')

        url = f'{API_URL}/bot{self.token}/{method}'

        if http_method == 'GET':
            async with self.session.get(url, params=data or {}) as resp:
                payload = await resp.json()
        else:
            async with self.session.post(url, json=data or {}) as resp:
                payload = await resp.json()

        self.logger.debug(payload)

        if not payload.get('ok'):
            raise TelegramAPIError(
                f'Telegram API error: '
                f'{payload.get("error_code")} {payload.get("description")}'
            )

        result = payload['result']

        if response_model is None:
            return result

        return response_model.model_validate(result)

    async def get_me(self) -> User: ...
