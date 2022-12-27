from flask.views import MethodView
from flask_smorest import Blueprint, abort
from CreateTransactionModel import db, Account, Acc_Transaction, AccountHolder, BankDetails
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import UploadTransactionsSchema, AccountStatementSchema, AccountTransactionsSchema, AccountTransactionQuerySchema
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from processfile import processfile

blp = Blueprint("Account Transactions", __name__,
                description="Manage Account Statements")


@blp.route("/statement/<int:account_id>")
class AccountStatement(MethodView):
    @cross_origin()
    @jwt_required()
    @blp.arguments(UploadTransactionsSchema)
    @blp.response(201, UploadTransactionsSchema)
    def post(self, statement_data, account_id):
        pass

    @cross_origin()
    @jwt_required()
    @blp.arguments(AccountTransactionQuerySchema, location="query")
    @blp.response(200, AccountStatementSchema)
    def get(self, statement_dates, account_id):
        account = Account.query.get_or_404(account_id)
        if (not "from_date" in statement_dates or statement_dates["from_date"] == "") and (not "to_date" in statement_dates or statement_dates["to_date"] == ""):
            transactions = account.transactions.order_by(
                Acc_Transaction.txn_date.desc(), Acc_Transaction.balance).all()
        else:
            if (not "to_date" in statement_dates or statement_dates["to_date"] == ""):
                transactions = account.transactions.filter(
                    Acc_Transaction.txn_date >= statement_dates["from_date"]).order_by(
                    Acc_Transaction.txn_date.desc(), Acc_Transaction.balance).all()
            else:
                if (not "from_date" in statement_dates or statement_dates["from_date"] == ""):
                    transactions = account.transactions.filter(
                        Acc_Transaction.txn_date <= statement_dates["to_date"]).order_by(
                        Acc_Transaction.txn_date.desc(), Acc_Transaction.balance).all()
                else:
                    transactions = account.transactions.filter(Acc_Transaction.txn_date.between(
                        statement_dates["from_date"], statement_dates["to_date"])).order_by(
                        Acc_Transaction.txn_date.desc(), Acc_Transaction.balance)
        return {"account_no": account.account_no, "transactions": transactions}
