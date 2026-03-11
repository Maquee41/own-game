from pydantic import BaseModel, Field


class AdminSchema(BaseModel):
    id_: int | None = Field(alias='id', default=None)
    email: str
    password: str = Field(exclude=True)
