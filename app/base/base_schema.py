from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    id_: int | None = Field(alias='id', default=None)
