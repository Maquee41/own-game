import typing

from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: 'Application'):
        from app.store.admin.accessor import AdminAccessor
        from app.store.bot.manager import BotManager
        from app.store.game.accessor import GameAccessor
        from app.store.tg_api.accessor import TelegramApiAccessor

        self.app = app
        self.bot_manager = BotManager(self.app)
        self.admins = AdminAccessor(app)
        self.game = GameAccessor(app)
        self.tg_api = TelegramApiAccessor(app)


def setup_store(app: 'Application'):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
