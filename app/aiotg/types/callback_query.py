from pydantic import BaseModel, Field

from .message import Message
from .user import User


class CallbackQuery(BaseModel):
    id: str
    from_user: User = Field(alias='from')
    chat_instance: str
    message: Message | None = None
    data: str | None = None
