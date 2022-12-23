from marshmallow import Schema, fields


class DateFormatSchema(Schema):
    date_id = fields.Int(dump_only=True)
    date_format = fields.Str(dump_only=True)
    desc = fields.Str(dump_only=True)
    py_date = fields.Str(dump_only=True)


class UserRegistration(Schema):
    user_id = fields.Int(dump_only=True)
    user_name = fields.Str(required=True)
    email_id = fields.Email(required=True, default_error_messages={
                            'invalid': 'Not a valid email address.'})
    password = fields.Str(load_only=True)
    u_active = fields.Bool(dump_only=True)
    admin = fields.Bool()


class UserLogin(Schema):
    user_id = fields.Int(dump_only=True)
    user_name = fields.Str(dump_only=True)
    email_id = fields.Email(required=True, default_error_messages={
                            'invalid': 'Not a valid email address.'})
    password = fields.Str(load_only=True)
    u_active = fields.Bool(dump_only=True)
    admin = fields.Bool()


class BanksSchema(Schema):
    bank_id = fields.Int(dump_only=True)
    bank_name = fields.Str(required=True)
    start_row = fields.Int(required=True)
    val_date_col = fields.Int(required=True)
    txn_date_col = fields.Int(required=True)
    chq_no_col = fields.Int(required=True)
    txn_rmrk_col = fields.Int(required=True)
    with_amt_col = fields.Int(required=True)
    crdt_amt_col = fields.Int(required=True)
    bal_col = fields.Int(required=True)
    date_id = fields.Int(required=True, load_only=True)
    date = fields.Nested(DateFormatSchema(), required=True, dump_only=True)
