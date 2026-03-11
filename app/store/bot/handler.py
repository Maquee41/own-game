from collections.abc import Awaitable, Callable

from app.store.bot.schemas import Update


class Handler:
    def __init__(self, func: Callable[[Update], Awaitable[None]], command: str):
        self.func = func
        self.command = command

    def check(self, update: Update) -> bool:
        if not update.message or not update.message.text:
            return False
        command = update.message.text.split()[0]
        return command == self.command
