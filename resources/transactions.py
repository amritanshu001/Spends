from flask.views import MethodView
from flask_smorest import Blueprint, abort
from CreateTransactionModel import (
    db,
    Account,
    Acc_Transaction,
    AccountHolder,
    BankDetails,
)
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import (
    UploadTransactionsSchema,
    AccountStatementSchema,
    AccountTransactionsSchema,
    AccountTransactionQuerySchema,
    UploadResponseSchema,
)
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from processfile import processfile
from flask_uploads import UploadSet, DOCUMENTS, UploadNotAllowed
import os
from flask import request
from dotenv import load_dotenv
load_dotenv()

blp = Blueprint(
    "Account Transactions", __name__, description="Manage Account Statements"
)

docs = UploadSet("statement", DOCUMENTS)


@blp.route("/statement/<int:account_id>")
class AccountStatement(MethodView):
    @cross_origin()
    @jwt_required()
    # @blp.arguments(UploadTransactionsSchema)
    @blp.response(201, UploadResponseSchema)
    def post(self, account_id):
        statement_data = request.files
        account = Account.query.get_or_404(account_id)
        try:
            statement_file = docs.save(statement_data["file"])
        except UploadNotAllowed:
            abort(400, message="Upload file in Microsoft Excel format only")
        else:
            df = processfile(docs.path(statement_file), account.bank)
            insert_suc = 0
            insert_fail = 0
            for indx, transaction in df.iterrows():
                acc_txn = Acc_Transaction(**dict(transaction))
                acc_txn.acc_id = account.account_id
                try:
                    db.session.add(acc_txn)
                    db.session.commit()
                except IntegrityError as e:
                    db.session.rollback()
                    insert_fail += 1
                    print(
                        "Transaction {} already exists. Skipping...".format(
                            transaction["txn_remarks"]
                        )
                    )
                else:
                    insert_suc += 1
            try:
                os.remove(docs.path(statement_file))
            except:
                print(
                    "Failed to delete the temp file from path {}".format(
                        docs.path(statement_file)
                    )
                )
        return {"pass_count": insert_suc, "fail_count": insert_fail}

    @cross_origin()
    @jwt_required()
    @blp.arguments(AccountTransactionQuerySchema, location="query")
    @blp.response(200, AccountStatementSchema)
    def get(self, statement_dates, account_id):
        account = Account.query.get_or_404(account_id)
        if (
            not "from_date" in statement_dates or statement_dates["from_date"] == ""
        ) and (not "to_date" in statement_dates or statement_dates["to_date"] == ""):
            transactions = account.transactions.order_by(
                Acc_Transaction.txn_date.desc(), Acc_Transaction.balance
            ).all()
        else:
            if not "to_date" in statement_dates or statement_dates["to_date"] == "":
                transactions = (
                    account.transactions.filter(
                        Acc_Transaction.txn_date >= statement_dates["from_date"]
                    )
                    .order_by(Acc_Transaction.txn_date.desc(), Acc_Transaction.balance)
                    .all()
                )
            else:
                if (
                    not "from_date" in statement_dates
                    or statement_dates["from_date"] == ""
                ):
                    transactions = (
                        account.transactions.filter(
                            Acc_Transaction.txn_date <= statement_dates["to_date"]
                        )
                        .order_by(
                            Acc_Transaction.txn_date.desc(), Acc_Transaction.balance
                        )
                        .all()
                    )
                else:
                    transactions = account.transactions.filter(
                        Acc_Transaction.txn_date.between(
                            statement_dates["from_date"], statement_dates["to_date"]
                        )
                    ).order_by(Acc_Transaction.txn_date.desc(), Acc_Transaction.balance)
        return {"account_no": account.account_no, "transactions": transactions}
