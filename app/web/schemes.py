from pydantic import BaseModel


class OkResponseSchema(BaseModel):
    status: str
    data: dict
