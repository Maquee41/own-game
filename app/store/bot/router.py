import typing
from collections.abc import Awaitable, Callable

from app.store.bot.schemas import Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Router:
    def __init__(self, app: 'Application') -> None:
        self.app = app
        self.message_handlers = []
        self.callback_handlers = []

    def command(self, cmd: str, chat_type: str | None = None):
        def decorator(func: Callable[[Update], Awaitable[None]]):
            self.message_handlers.append(
                {
                    'type': 'command',
                    'command': cmd,
                    'chat_type': chat_type,
                    'func': func,
                }
            )
            return func

        return decorator

    def callback(self, prefix: str):
        def decorator(func):
            self.callback_handlers.append(
                {
                    'prefix': prefix,
                    'func': func,
                }
            )
            return func

        return decorator

    async def dispatch(self, update: Update):
        if update.message:
            await self._dispatch_message(update)
            return

        if update.callback_query:
            await self._dispatch_callback(update)
            return

    async def _dispatch_message(self, update: Update):
        message = update.message
        if not message or not message.text:
            return

        command = message.text.split()[0]
        chat_type = message.chat.type_.value

        for handler in self.message_handlers:
            if handler['type'] != 'command':
                continue
            if handler['command'] != command:
                continue
            if handler['chat_type'] and handler['chat_type'] != chat_type:
                continue

            await handler['func'](update)
            return

    async def _dispatch_callback(self, update: Update):
        callback = update.callback_query
        if not callback or not callback.data:
            return

        for handler in self.callback_handlers:
            if callback.data.startswith(handler['prefix']):
                await handler['func'](update)
                return
