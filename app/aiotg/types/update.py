from pydantic import BaseModel

from app.aiotg.types.callback_query import CallbackQuery
from app.aiotg.types.message import Message


class Update(BaseModel):
    update_id: int
    message: Message | None = None
    callback_query: CallbackQuery | None = None
