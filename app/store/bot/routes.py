import typing

from app.store.bot.handlers.callbacks import register_callback_handlers
from app.store.bot.handlers.group import register_group_handlers
from app.store.bot.handlers.private import register_private_handlers
from app.store.bot.router import Router

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_router(app: 'Application') -> Router:
    router = Router(app)

    register_private_handlers(router)
    register_group_handlers(router)
    register_callback_handlers(router)

    return router
