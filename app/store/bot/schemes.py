import enum

from pydantic import BaseModel, Field


class ChatTypeEnum(enum.Enum):
    CHANNEL = 'channel'
    GROUP = 'group'
    PRIVATE = 'private'
    SUPERGROUP = 'supergroup'


class Chat(BaseModel):
    id_: int = Field(alias='id')
    type_: ChatTypeEnum = Field(alias='type')
    title: str | None = None


class User(BaseModel):
    id_: int = Field(alias='id')
    is_bot: bool
    first_name: str
    username: str
    language_code: str


class MessageEntityEnum(enum.Enum):
    BOT_COMMAND = 'bot_command'
    CASHTAG = 'cashtag'
    EMAIL = 'email'
    HASHTAG = 'hashtag'
    MENTION = 'mention'
    PHONE_NUMBER = 'phone_number'
    URL = 'url'


class MessageEntity(BaseModel):
    type_: MessageEntityEnum | None = Field(alias='type', default=None)


class Message(BaseModel):
    chat: Chat
    date: int
    message_id: int
    from_: User | None = Field(alias='from', default=None)
    text: str | None = None
    entities: list[MessageEntity] | None = None


class Update(BaseModel):
    update_id: int
    message: Message | None = None


class UpdateList(BaseModel):
    ok: bool
    result: list[Update] | None = None
