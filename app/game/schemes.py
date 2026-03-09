from pydantic import model_validator

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
