from flask.views import MethodView
from flask_smorest import Blueprint, abort
from CreateTransactionModel import db, Account, Acc_Transaction, AccountHolder, BankDetails
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import AccountsSchema, UpdateAccountSchema
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

blp = Blueprint("Account Transactions", __name__,description="Manage Account Statements")
