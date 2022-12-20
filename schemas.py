from marshmallow import Schema, fields


class DateFormatSchema(Schema):
    date_id = fields.Int(dump_only=True)
    date_format = fields.Str(dump_only=True)
    desc = fields.Str(dump_only=True)
    py_date = fields.Str(dump_only=True)
