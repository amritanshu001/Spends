from flask.views import MethodView
from flask_smorest import Blueprint, abort
from CreateTransactionModel import db, Account, Acc_Transaction, AccountHolder, BankDetails
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import AccountsSchema, UpdateAccountSchema
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

blp = Blueprint("Account Management", __name__,
                description="Manage User Accounts")


@blp.route("/accounts")
class AccountsManagement(MethodView):
    @cross_origin()
    @jwt_required()
    @blp.response(200, AccountsSchema(many=True))
    def get(self):
        id = get_jwt_identity()
        user = AccountHolder.query.get_or_404(id)
        accounts = user.accounts.filter_by(active=True).all()
        return accounts

    @cross_origin()
    @jwt_required()
    @blp.arguments(AccountsSchema)
    @blp.response(201, AccountsSchema)
    def post(self, account_data):
        id = get_jwt_identity()
        user = AccountHolder.query.get_or_404(id)
        bank = BankDetails.query.get_or_404(account_data['bank'])
        account = Account.query.filter_by(
            account_no=account_data["account_no"]).first()

        if account:
            existing_user = account.users.filter_by(user_id=id).first()
            if existing_user:
                abort(403, message="Account already assigned to this user")
            if not account.joint:
                abort(406, message="This account is already assigned to another user")
            account.users.append(user)
            try:
                db.session.add(account)
                db.session.commit()
            except SQLAlchemyError as q:
                db.session.rollback()
                abort(400, message=str(q))
            else:
                return account
        new_account = Account()
        new_account.account_no = account_data["account_no"]
        new_account.bank = bank.bank_id
        new_account.joint = account_data["joint"]
        new_account.users.append(user)

        try:
            db.session.add(new_account)
            db.session.commit()
        except SQLAlchemyError as q:
            db.session.rollback()
            abort(400, message=str(q))
        else:
            return new_account


@blp.route("/accounts/<int:account_id>")
class AccountManagement(MethodView):
    @cross_origin()
    @jwt_required()
    @blp.response(200, AccountsSchema)
    def get(self, account_id):
        account = Account.query.get(account_id)
        return account

    @cross_origin()
    @jwt_required()
    @blp.arguments(UpdateAccountSchema)
    @blp.response(201, AccountsSchema)
    def put(self, account_data, account_id):
        if "joint" not in account_data:
            abort(404, message="Required Attribute missing")
        account = Account.query.get_or_404(account_id)
        account.joint = account_data["joint"]

        try:
            db.session.add(account)
            db.session.commit()
        except SQLAlchemyError as q:
            db.session.rollback()
            abort(400, message=str(q))
        else:
            return account

    @cross_origin()
    @jwt_required()
    def delete(self, account_id):
        user_id = get_jwt_identity()
        user = AccountHolder.query.get(user_id)
        account = user.accounts.filter_by(account_id=account_id).first()
        if not account:
            abort(404, message="Account not found for this user")
        account.active = False

        try:
            db.session.add(account)
            db.session.commit()
        except SQLAlchemyError as q:
            db.session.rollback()
            abort(400, message=str(q))
        else:
            return {"message": "Account deactivated"}, 201
