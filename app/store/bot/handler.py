from app.store.bot.schemes import Update


class Handler:
    def __init__(self, func, command):
        self.func = func
        self.command = command

    def check(self, update: Update) -> bool:
        return update.message.text.startswith(self.command)
