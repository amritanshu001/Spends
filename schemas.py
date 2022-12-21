from marshmallow import Schema, fields


class DateFormatSchema(Schema):
    date_id = fields.Int(dump_only=True)
    date_format = fields.Str(dump_only=True)
    desc = fields.Str(dump_only=True)
    py_date = fields.Str(dump_only=True)


class AccountHolderSchema(Schema):
    user_id = fields.Int(dump_only=True)
    user_name = fields.Str(required=True)
    email_id = fields.Email(required=True, default_error_messages={
                            'invalid': 'Not a valid email address.'})
    password = fields.Str(load_only=True)
    u_active = fields.Bool(dump_only=True)
    admin = fields.Bool()
