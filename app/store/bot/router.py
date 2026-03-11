from app.store.bot.handler import Handler
from app.store.bot.schemes import Update


class Router:
    def __init__(self) -> None:
        self.handlers: list[Handler] = []

    def command(self, cmd):
        def decorator(func):
            self.handlers.append(Handler(func, cmd))
            return func

        return decorator

    async def dispatch(self, update: Update):
        for handler in self.handlers:
            if handler.check(update):
                await handler.func(update)
