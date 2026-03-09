from dataclasses import dataclass


@dataclass
class Chat:
    id_: int
    title: str | None = None


@dataclass
class User:
    id_: int
    is_bot: bool
    first_name: str
    username: str
    language_code: str


@dataclass
class MessageEntity:
    type_: str


@dataclass
class Message:
    chat: Chat
    from_: User
    text: str
    message_id: int | None = None
    entities: list[MessageEntity] | None = None
    date: int | None = None


@dataclass
class Update:
    update_id: int
    message: Message
