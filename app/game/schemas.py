from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.base.base_schema import BaseSchema


class UserSchema(BaseSchema):
    username: str
    tg_id: int
    score: float


class ThemeSchema(BaseSchema):
    title: str


class AnswerSchema(BaseSchema):
    title: str
    is_correct: bool


class QuestionSchema(BaseSchema):
    title: str
    theme_id: int
    answers: list[AnswerSchema]

    @model_validator(mode='after')
    def check_answers(self):
        if len(self.answers) < 1:
            raise ValueError('Question must contain at least one answer')

        if not any(a.is_correct for a in self.answers):
            raise ValueError('At least one answer must be correct')

        return self


class Player(BaseModel):
    tg_id: int
    confirmed: bool = False
    score: int = 0


class RoomState(BaseModel):
    message_id: int | None = None
    players: list[Player] = Field(default_factory=list)
    theme_id: int | None = None
    current_question_id: int | None = None
    question_ids: list[int] = Field(default_factory=list)
    question_opened_at: datetime | None = None
    answered_users_ids: list[int] = Field(default_factory=list)
    user_id_answer: int | None = None
    button_enable: bool = False
    deadline: datetime | None = None
