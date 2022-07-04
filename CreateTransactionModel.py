from flask import Flask
from flask_sqlalchemy import SQLAlchemy as sql
from sqlalchemy import ForeignKey
from databaseconnect import get_engine
from datetime import datetime
from sqlalchemy.exc import NoReferencedTableError
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = get_engine()[0]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = sql(app)
migrate = Migrate()

db.init_app(app)
migrate.init_app(app,db)

class BankDetails(db.Model):
    __tablename__ = 'bank_details'
    bank_id = db.Column(db.Integer, nullable = False, primary_key = True, autoincrement = True)
    bank_name = db.Column(db.String(200), nullable = False, unique = True)
    start_row = db.Column(db.Integer)
    val_date_col = db.Column(db.Integer)
    txn_date_col = db.Column(db.Integer)
    chq_no_col = db.Column(db.Integer)
    txn_rmrk_col = db.Column(db.Integer)
    with_amt_col = db.Column(db.Integer)
    crdt_amt_col = db.Column(db.Integer)
    bal_col = db.Column(db.Integer)
    date_id = db.Column(db.Integer, db.ForeignKey('dateformat.date_id'))
    
    # one to many relationship
    accounts = db.relationship('Account',backref = 'bank_details')

    def __repr__(self):
        return f'<Bank {self.bank_name}>'

class DateFormat(db.Model):
    __tablename__ = 'dateformat'
    date_id = db.Column(db.Integer, nullable = False, primary_key = True, autoincrement = True)
    date_format = db.Column(db.String(20),nullable = False, unique = True)
    desc = db.Column(db.String(200),nullable = False)
    py_date = db.Column(db.String(20), nullable = False)

account_users = db.Table('account_users',
                db.Column('user_id', db.Integer, db.ForeignKey('accountholder.user_id'), primary_key = True),
                db.Column('account_id', db.Integer, db.ForeignKey('account.account_id'), primary_key = True)
            )

class AccountHolder(db.Model):
    __tablename__ = 'accountholder'
    user_id = db.Column(db.Integer, nullable = False, primary_key = True, autoincrement = True)
    user_name = db.Column(db.String(200), nullable = False)
    email_id = db.Column(db.String(200), nullable = False, unique = True)
    password = db.Column(db.String(500), nullable = False)
    u_active = db.Column(db.Boolean, default = True)
    admin = db.Column(db.Boolean, default = False)
    #m:n relationships
    accounts = db.relationship('Account', secondary = account_users, back_populates = "users")
    #banks = db.relationship('BankDetails', secondary = bank_users)


    def __repr__(self):
        return f'<User {self.user_name}>'


class Account(db.Model):
    __tablename__ = 'account'
    account_id = db.Column(db.Integer, nullable = False, primary_key = True, autoincrement = True)
    account_no = db.Column(db.String(20), nullable = False, unique = True)
    active = db.Column(db.Boolean, default = True)
    joint = db.Column(db.Boolean, default = False)
    #Foreign Key for 1:n relation
    bank  = db.Column(db.Integer, db.ForeignKey('bank_details.bank_id'), nullable = False)
    # one to many relationship
    users = db.relationship('AccountHolder', secondary = account_users, back_populates = "accounts")
    transactions = db.relationship('Acc_Transaction',backref = 'account')

    def __repr__(self):
        return f'<Account {self.account_no}>'

class Acc_Transaction(db.Model):
    __tablename__ = 'acc_transaction'
    txn_id = db.Column(db.Integer, nullable = False, primary_key = True, autoincrement = True)
    value_date = db.Column(db.DateTime, nullable = False)
    txn_date = db.Column(db.DateTime, nullable = False)
    txn_remarks = db.Column(db.Text(), nullable = False)
    cheque_no = db.Column(db.String(20))
    withdrawal_amt = db.Column(db.Float)
    deposit_amt = db.Column(db.Float)
    balance = db.Column(db.Float, nullable = False)
    #Foreign Key for 1:n relation
    acc_id  = db.Column(db.Integer, db.ForeignKey('account.account_id'), nullable = False)

    def __repr__(self):
        return f'<Transaction {self.txn_id}>'



if __name__ == '__main__':

    db.create_all()