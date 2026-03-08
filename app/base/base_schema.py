from marshmallow import Schema, fields


class BaseSchema(Schema):
    id = fields.Int(required=False)
