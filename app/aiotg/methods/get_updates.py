from typing import Any

from app.aiotg.client.bot import Bot
from app.aiotg.types.update import Update


async def get_updates(
    bot: Bot,
    offset: int | None = None,
    timeout: int = 30,
    allowed_updates: list[str] | None = None,
) -> list[Update]:
    data: dict[str, Any] = {
        'timeout': timeout,
    }

    if offset is not None:
        data['offset'] = offset

    if allowed_updates is not None:
        data['allowed_updates'] = allowed_updates

    result = await bot.request(
        'getUpdates',
        data=data,
        http_method='GET',
    )

    return [Update.model_validate(item) for item in result]
