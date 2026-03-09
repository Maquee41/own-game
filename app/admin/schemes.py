from pydantic import BaseModel, Field


class AdminSchema(BaseModel):
    id: int | None = None
    email: str
    password: str = Field(exclude=True)
