from pydantic import BaseModel, Field


class Chat(BaseModel):
    id_: int = Field(alias='id')
    type_: str = Field(alias='type')
    title: str | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
