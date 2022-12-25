from flask.views import MethodView
from flask_smorest import Blueprint, abort
from CreateTransactionModel import db, Account, Acc_Transaction, AccountHolder, BankDetails
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import UploadTransactionsSchema, AccountStatementSchema
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from processfile import processfile

blp = Blueprint("Account Transactions", __name__,
                description="Manage Account Statements")


@blp.route("/statement")
class AccountStatement(MethodView):
    @cross_origin()
    @jwt_required()
    @blp.arguments(UploadTransactionsSchema)
    @blp.response(201, UploadTransactionsSchema)
    def post(self, statement_data):
        pass
