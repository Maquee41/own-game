from marshmallow import fields

from app.base.base_schema import BaseSchema


class UserSchema(BaseSchema):
    username = fields.Str(required=True)
    tg_id = fields.Int(required=True)
    score = fields.Float(required=True)


class ThemeSchema(BaseSchema):
    title = fields.Str(required=True)


class AnswerSchema(BaseSchema):
    title = fields.Str(required=True)
    is_correct = fields.Bool(required=True)


class QuestionSchema(BaseSchema):
    title = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    answers = fields.Nested(AnswerSchema, many=True, required=True)
