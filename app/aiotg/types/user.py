from pydantic import BaseModel, Field


class User(BaseModel):
    id_: int = Field(alias='id')
    is_bot: bool
    first_name: str
    last_name: str | None = None
    username: str | None = None
    can_join_groups: bool | None = None
    can_read_all_group_messages: bool | None = None
    supports_inline_queries: bool | None = None
    has_main_web_app: bool | None = None
