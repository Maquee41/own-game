from app.store.bot.router import Router
from app.store.bot.schemas import Update


def register_callback_handlers(router: Router) -> None:
    @router.callback('game:')
    async def game_callback(update): ...

    @router.callback('game:join')
    async def cb_join(update: Update):
        callback = update.callback_query
        chat_id = callback.message.chat.id_  # noqa: F841
        user_id = callback.from_.id_  # noqa: F841

        # TODO
        # add player in the match
        # update game message
        ...
