
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField, EmailField, SelectField, Form, FormField, FieldList, BooleanField, SubmitField, IntegerField, FileField, DecimalField, ValidationError
from wtforms.validators import InputRequired, Length, NumberRange, Optional, EqualTo
from CreateTransactionModel import db, BankDetails, DateFormat
from pathlib import Path
from wtforms.fields import DateField


class LoginForm(FlaskForm):
    email = EmailField("Email Id", validators=[InputRequired(message = "Email cannot be blank"),
            Length(min= 8, max= 200)
    ])
    password = PasswordField("Password", validators=[InputRequired(message = "Password cannot be blank"),
            Length(min= 8, max= 50),
    ])

class DelBankData(Form):
    bankname = StringField("Bank", render_kw = {'readonly':True})
    accountno = StringField("Account No.", render_kw = {'readonly':True})
    deactivate = BooleanField("Deactivate")

class BankData(Form):
    bankname = SelectField("Bank",coerce=int, choices=[("0","---")])
    accountno = StringField("Account No.",validators=[
        Length(max = 20)
    ])
    jointacc = BooleanField("Joint")
    refresh = SubmitField("Refresh")


class RegisterForm(FlaskForm):
    username = StringField("User Name", validators=[InputRequired(message = "User Name cannot be blank"),
            Length(min = 8, max= 200)
    ])
    password = PasswordField("Password", validators=[InputRequired(message = "Password cannot be blank"),
            Length(min= 8, max= 50),
            EqualTo('repassword', message = "**Passwords must match")
    ])
    email = EmailField("Email Id", validators=[InputRequired(message = "Email cannot be blank"),
            Length(min= 8, max= 200)
    ])
    repassword = PasswordField("Re-enter Password", validators=[InputRequired()])

class AddAccount(FlaskForm):
    banks = FieldList(FormField(BankData),min_entries=3)
    add_acc = SubmitField("Add Accounts")

class DelAccount(FlaskForm):
    bank_det = FieldList(FormField(DelBankData), min_entries=0)
    del_acc = SubmitField("Delete Accounts") 

class BankForm(FlaskForm):

    bank_name = StringField("Bank Name", validators=[InputRequired()])
    start_row  = IntegerField("Starting from [row]",validators=[InputRequired(),
    NumberRange(min = 1, message = "Cannot be less than 1")])
    val_date_col = IntegerField("Value Date [col]",validators=[InputRequired(),
    NumberRange(min = 1, message = "Cannot be less than 1")])
    txn_date_col = IntegerField("Transaction Date [col]",validators=[InputRequired(),
    NumberRange(min = 1, message = "Cannot be less than 1")])
    chq_no_col = IntegerField("Cheque No. [col]",validators=[InputRequired(),
    NumberRange(min = 1, message = "Cannot be less than 1")])
    txn_rmrk_col = IntegerField("Remarks [col]",validators=[InputRequired(),
    NumberRange(min = 1, message = "Cannot be less than 1")])
    with_amt_col = IntegerField("Withdrawl Amount [col]",validators=[InputRequired(),
    NumberRange(min = 1, message = "Cannot be less than 1")])
    crdt_amt_col = IntegerField("Credit Amount [col]",validators=[InputRequired(),
    NumberRange(min = 1, message = "Cannot be less than 1")])
    bal_col = IntegerField("Balance [col]",validators=[InputRequired(),
    NumberRange(min = 1, message = "Cannot be less than 1")])
    date_id = SelectField("Date Format",coerce = int, validators=[InputRequired()], choices=[('0','---')])
    add_bank = SubmitField("Add Bank")

class BankList(FlaskForm):
    bankname = SelectField("Bank",coerce=int, choices=[("0","---")])
    refresh = SubmitField("Refresh")

class Upload(FlaskForm):
    select_account = SelectField("Select Account", validators=[InputRequired()], coerce=int, choices=[])
    file = FileField("File Path", validators=[InputRequired()])
    upload = SubmitField("Upload Statement")

class Top5(Form):
    txn_no = IntegerField("Transaction Number", validators=[NumberRange(min=1)], render_kw = {'readonly':True})
    txn_date = DateField("Transaction Date", render_kw = {'readonly':True})#,format='%d-%b-%Y')
    txn_amt = DecimalField("Transaction Amount", render_kw = {'readonly':True})
    txn_remarks = StringField("Remarks", render_kw = {'readonly':True})

class SpendsAnalysis(FlaskForm):
    select_account = SelectField("Select Account", validators=[InputRequired()], coerce=int, choices=[])
    frm_date = DateField("From Date", validators=[InputRequired()])
    to_date = DateField("To Date",validators=[InputRequired()])
    from_amt = DecimalField("From Amount", validators=[Optional()])
    to_amt = DecimalField("To Amount", validators=[Optional()])
    srch_remarks = StringField("Transaction Remark contains", validators=[Optional()])
    opening_bal = DecimalField(label="Opening Balance", render_kw = {'readonly':True})
    outgoing = DecimalField("Outgoing", render_kw = {'readonly':True})
    incoming = DecimalField("Incoming", render_kw = {'readonly':True})
    incoming_txn = IntegerField(render_kw = {'readonly':True})
    outgoing_txn = IntegerField(render_kw = {'readonly':True})
    incoming_avg = DecimalField( render_kw = {'readonly':True})
    outgoing_avg = DecimalField( render_kw = {'readonly':True})
    balance = DecimalField( render_kw = {'readonly':True})
    closing_bal = DecimalField(label="Closing Balance", render_kw = {'readonly':True})
    top_5_credit = FieldList(FormField(Top5), max_entries=5, render_kw = {'readonly':True})
    top_5_debit = FieldList(FormField(Top5), max_entries=5, render_kw = {'readonly':True})
    top5_share_credit = DecimalField("Top 5 Share", render_kw = {'readonly':True})
    top5_share_debit = DecimalField("Top 5 Share", render_kw = {'readonly':True})
    spend = SubmitField("Spend Analysis")





