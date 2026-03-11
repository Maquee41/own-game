from app.store.bot.router import Router
from app.store.bot.schemas import Update


def register_group_handlers(router: Router) -> None:
    @router.command('/startgame', chat_type='group')
    async def cmd_start_game(update: Update):
        message = update.message
        chat_id = message.chat.id_  # noqa: F841

        # TODO
        # create match via GameStore
        # send one message with inline buttons
        ...
