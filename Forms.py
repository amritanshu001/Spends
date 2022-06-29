from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField, EmailField, SelectField, Form, FormField, FieldList, BooleanField, SubmitField
from wtforms.validators import InputRequired, Length
from CreateTransactionModel import db, BankDetails

class LoginForm(FlaskForm):
    email = EmailField("Email Id", validators=[InputRequired(message = "Email cannot be blank"),
            Length(min= 8, max= 200)
    ])
    password = PasswordField("Password", validators=[InputRequired(message = "Password cannot be blank"),
            Length(min= 8, max= 50)
    ])

class DelBankData(Form):
    bankname = StringField("Bank", render_kw = {'readonly':True})
    accountno = StringField("Account No.", render_kw = {'readonly':True})
    deactivate = BooleanField("Deactivate")

class BankData(Form):
    bankname = SelectField("Bank",coerce=int, choices=[("0","---")] + [(bank.bank_id, bank.bank_name) for bank in BankDetails.query.all()])
    accountno = StringField("Account No.",validators=[
        Length(max = 20)
    ])
    jointacc = BooleanField("Joint")

class RegisterForm(FlaskForm):
    username = StringField("User Name", validators=[InputRequired(message = "User Name cannot be blank"),
            Length(min = 8, max= 200)
    ])
    password = PasswordField("Password", validators=[InputRequired(message = "Password cannot be blank"),
            Length(min= 8, max= 50)
    ])
    email = EmailField("Email Id", validators=[InputRequired(message = "Email cannot be blank"),
            Length(min= 8, max= 200)
    ])

class AddAccount(FlaskForm):
    banks = FieldList(FormField(BankData),min_entries=3)
    add_acc = SubmitField("Add Accounts")

class DelAccount(FlaskForm):
    bank_det = FieldList(FormField(DelBankData), min_entries=0)
    del_acc = SubmitField("Delete Accounts") 