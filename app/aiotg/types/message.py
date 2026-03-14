from pydantic import BaseModel, Field

from app.aiotg.types.chat import Chat
from app.aiotg.types.user import User


class Message(BaseModel):
    id_: int = Field(alias='message_id')
    date: int
    chat: Chat
    from_user: User | None = Field(alias='from', default=None)
    text: str | None = None
