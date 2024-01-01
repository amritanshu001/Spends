from marshmallow import Schema, fields


class DateFormatSchema(Schema):
    date_id = fields.Int(dump_only=True)
    date_format = fields.Str(required=True)
    desc = fields.Str(required=True)
    py_date = fields.Str(required=True)


class UserRegistration(Schema):
    user_id = fields.Int(dump_only=True)
    user_name = fields.Str(required=True)
    email_id = fields.Email(
        required=True, default_error_messages={"invalid": "Not a valid email address."}
    )
    password = fields.Str(load_only=True)


class PasswordResetRequest(Schema):
    email_id = fields.Email(
        required=True, default_error_messages={"invalid": "Not a valid email address."}
    )
    site_url = fields.Url(load_only=True)
    userHash = fields.String(dump_only=True)


class PasswordReset(Schema):
    userHash = fields.String(load_only=True, required=True)
    newPassword = fields.String(load_only=True)
    email_id = fields.Email(dump_only=True)


class UserLogin(Schema):
    user_id = fields.Int(dump_only=True)
    user_name = fields.Str(dump_only=True)
    email_id = fields.Email(
        required=True, default_error_messages={"invalid": "Not a valid email address."}
    )
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


class AccountsSchema(Schema):
    account_id = fields.Int(dump_only=True)
    account_no = fields.Str(required=True)
    active = fields.Boolean(dump_only=True)
    joint = fields.Boolean(required=True)
    bank = fields.Int(required=True, load_only=True)
    bank_dets = fields.Nested(BanksSchema(), required=True, dump_only=True)


class InactiveAccountsSchema(AccountsSchema):
    user_emails = fields.Str(required=True)


class AccountTransactionsSchema(Schema):
    txn_id = fields.Int(dump_only=True)
    value_date = fields.DateTime(required=True, dump_only=True)
    txn_date = fields.DateTime(required=True, dump_only=True)
    txn_remarks = fields.String(required=True, dump_only=True)
    cheque_no = fields.String(dump_only=True)
    withdrawal_amt = fields.Float(dump_only=True)
    deposit_amt = fields.Float(dump_only=True)
    balance = fields.Float(required=True, dump_only=True)


class AccountTransactionQuerySchema(Schema):
    from_date = fields.Str()
    to_date = fields.Str()


class AccountStatementSchema(AccountsSchema):
    account_no = fields.Str(dump_only=True)
    transactions = fields.List(
        fields.Nested(AccountTransactionsSchema()), dump_only=True
    )


class AccountUsersSchema(AccountsSchema):
    users = fields.List(
        fields.Nested(UserRegistration()), required=True, dump_only=True
    )


class UpdateAccountSchema(Schema):
    joint = fields.Boolean(load_only=True)
    active = fields.Boolean(load_only=True)


class UploadTransactionsSchema(Schema):
    upload_file = fields.Field(load_only=True, required=True)


class UploadResponseSchema(Schema):
    pass_count = fields.Int(required=True, dump_only=True)
    fail_count = fields.Int(required=True, dump_only=True)
