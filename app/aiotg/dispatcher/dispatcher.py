from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from app.aiotg.client.bot import Bot
from app.aiotg.methods.get_updates import get_updates
from app.aiotg.types.update import Update

CommandHandler = Callable[[Bot, Update], Awaitable[None]]
CallbackHandler = Callable[[Bot, Update], Awaitable[None]]


@dataclass(slots=True)
class CommandRoute:
    handler: CommandHandler
    chat_types: set[str] | None = None


@dataclass(slots=True)
class CallbackRoute:
    handler: CallbackHandler
    chat_types: set[str] | None = None


class Dispatcher:
    def __init__(self) -> None:
        self.command_handlers: dict[str, list[CommandRoute]] = {}
        self.callback_handlers: dict[str, list[CallbackRoute]] = {}

    def command(self, name: str, chat_types: set[str] | None = None):
        def decorator(func: CommandHandler):
            routes = self.command_handlers.setdefault(name, [])
            routes.append(CommandRoute(handler=func, chat_types=chat_types))
            return func

        return decorator

    def callback(self, prefix: str, chat_types: set[str] | None = None):
        def decorator(func: CallbackHandler):
            routes = self.callback_handlers.setdefault(prefix, [])
            routes.append(CallbackRoute(handler=func, chat_types=chat_types))
            return func

        return decorator

    async def feed_update(self, bot: Bot, update: Update) -> None:
        if update.message and update.message.text:
            text = update.message.text.strip()
            chat_type = update.message.chat.type_

            if text.startswith('/'):
                command = text.split()[0].split('@')[0][1:]
                routes = self.command_handlers.get(command, [])

                for route in routes:
                    if route.chat_types is None or chat_type in route.chat_types:
                        await route.handler(bot, update)
                        return

        if update.callback_query and update.callback_query.data:
            data = update.callback_query.data

            chat_type: str | None = None
            if update.callback_query.message is not None:
                chat_type = update.callback_query.message.chat.type_

            for prefix, routes in self.callback_handlers.items():
                if data.startswith(prefix):
                    for route in routes:
                        if route.chat_types is None or chat_type in route.chat_types:
                            await route.handler(bot, update)
                            return

    async def start_polling(self, bot: Bot) -> None:
        offset: int | None = None

        while True:
            updates = await get_updates(
                bot,
                offset=offset,
                timeout=30,
                allowed_updates=['message', 'callback_query'],
            )

            for update in updates:
                offset = update.update_id + 1
                await self.feed_update(bot, update)
