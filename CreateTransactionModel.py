from flask import Flask
from flask_sqlalchemy import SQLAlchemy as sql
from sqlalchemy.sql import func
from databaseconnect import get_engine
from utils import db

class BankDetails(db.Model):
    __tablename__ = "bank_details"
    bank_id = db.Column(
        db.Integer, nullable=False, primary_key=True, autoincrement=True
    )
    bank_name = db.Column(db.String(200), nullable=False, unique=True)
    start_row = db.Column(db.Integer)
    val_date_col = db.Column(db.Integer)
    txn_date_col = db.Column(db.Integer)
    chq_no_col = db.Column(db.Integer)
    txn_rmrk_col = db.Column(db.Integer)
    with_amt_col = db.Column(db.Integer)
    crdt_amt_col = db.Column(db.Integer)
    bal_col = db.Column(db.Integer)
    date_id = db.Column(db.Integer, db.ForeignKey("dateformat.date_id"))
    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    date = db.relationship("DateFormat", backref="bank_details")

    # one to many relationship
    accounts = db.relationship("Account", back_populates="bank_dets", lazy="dynamic")

    def __repr__(self):
        return f"<Bank {self.bank_name}>"


class DateFormat(db.Model):
    __tablename__ = "dateformat"
    date_id = db.Column(
        db.Integer, nullable=False, primary_key=True, autoincrement=True
    )
    date_format = db.Column(db.String(20), nullable=False, unique=True)
    desc = db.Column(db.String(200), nullable=False)
    py_date = db.Column(db.String(20), nullable=False)
    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Date Format {self.date_format}"


account_users = db.Table(
    "account_users",
    db.Column(
        "user_id", db.Integer, db.ForeignKey("accountholder.user_id"), primary_key=True
    ),
    db.Column(
        "account_id", db.Integer, db.ForeignKey("account.account_id"), primary_key=True
    ),
)


class AccountHolder(db.Model):
    __tablename__ = "accountholder"
    user_id = db.Column(
        db.Integer, nullable=False, primary_key=True, autoincrement=True
    )
    user_name = db.Column(db.String(200), nullable=False)
    email_id = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    u_active = db.Column(db.Boolean, default=True)
    admin = db.Column(db.Boolean, default=False)
    reset_hash = db.Column(db.String(200))
    reset_expiry = db.Column(db.DateTime)
    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    last_logged_in = db.Column(db.DateTime(timezone=True))
    # m:n relationships
    accounts = db.relationship(
        "Account", secondary=account_users, back_populates="users", lazy="dynamic"
    )

    def __repr__(self):
        return f"<User {self.user_name}>"


class Account(db.Model):
    __tablename__ = "account"
    account_id = db.Column(
        db.Integer, nullable=False, primary_key=True, autoincrement=True
    )
    account_no = db.Column(db.String(20), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)
    joint = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    # Foreign Key for 1:n relation
    bank = db.Column(db.Integer, db.ForeignKey("bank_details.bank_id"), nullable=False)
    bank_dets = db.relationship("BankDetails", back_populates="accounts")
    # one to many relationship
    users = db.relationship(
        "AccountHolder",
        secondary=account_users,
        back_populates="accounts",
        lazy="joined",
    )
    transactions = db.relationship(
        "Acc_Transaction", back_populates="account_dets", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Account {self.account_no}>"

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}


class Acc_Transaction(db.Model):
    __tablename__ = "acc_transaction"
    txn_id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    value_date = db.Column(db.DateTime, nullable=False)
    txn_date = db.Column(db.DateTime, nullable=False)
    txn_remarks = db.Column(db.Text(), nullable=False)
    cheque_no = db.Column(db.Text())
    withdrawal_amt = db.Column(db.Float)
    deposit_amt = db.Column(db.Float)
    balance = db.Column(db.Float, nullable=False)
    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    # Foreign Key for 1:n relation
    acc_id = db.Column(db.Integer, db.ForeignKey("account.account_id"), nullable=False)
    account_dets = db.relationship("Account", back_populates="transactions")
    __table_args__ = (
        db.UniqueConstraint(
            "value_date",
            "txn_date",
            "txn_remarks",
            "withdrawal_amt",
            "deposit_amt",
            "balance",
            "cheque_no",
            name="unique_txn",
        ),
    )

    def __repr__(self):
        return f"<{self.txn_id}:{self.txn_date} - {self.txn_remarks}>"


if __name__ == "__main__":
    db.create_all()
