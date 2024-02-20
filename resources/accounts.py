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
from sqlalchemy.orm import joinedload
from schemas import AccountsSchema, UpdateAccountSchema, InactiveAccountsSchema
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

blp = Blueprint("Account Management", __name__, description="Manage User Accounts")


@blp.route("/accounts")
class AccountsManagement(MethodView):
    @cross_origin()
    @jwt_required()
    @blp.response(200, AccountsSchema(many=True))
    def get(self):
        id = get_jwt_identity()
        user = AccountHolder.query.get_or_404(id)
        accounts = user.accounts.filter_by(active=True).order_by(Account.account_id)
        return accounts

    @cross_origin()
    @jwt_required()
    @blp.arguments(AccountsSchema)
    @blp.response(201, AccountsSchema)
    def post(self, account_data):
        id = get_jwt_identity()
        user = AccountHolder.query.get_or_404(id)
        bank = BankDetails.query.get_or_404(account_data["bank"])
        account = Account.query.filter_by(account_no=account_data["account_no"]).first()

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


@blp.route("/admin/accounts")
class GetAdminAccounts(MethodView):
    @cross_origin()
    @jwt_required()
    @blp.response(200, InactiveAccountsSchema(many=True))
    def get(self):
        jwt = get_jwt()
        if not jwt.get("admin"):
            abort(401, message="Only Admin has access to this feature")
        inactive_accounts = (
            Account.query.options(joinedload(Account.users))
            .filter(Account.active == False)
            .all()
        )
        incative_list = []

        for account in inactive_accounts:
            output_acc = InactiveAccountsSchema()
            output_acc.account_id = account.account_id
            output_acc.account_no = account.account_no
            output_acc.active = account.active
            output_acc.joint = account.joint
            output_acc.bank = account.bank
            output_acc.bank_dets = account.bank_dets
            output_acc.created_on = account.created_on
            output_acc.updated_on = account.updated_on
            holders = ""
            for user in account.users:
                holders = holders + user.email_id + ","
            output_acc.user_emails = holders.rstrip(",")
            incative_list.append(output_acc)
        return incative_list


@blp.route("/admin/accounts/<int:account_id>")
class ManageAdminAccounts(MethodView):
    @cross_origin()
    @jwt_required()
    def put(self, account_id):
        print(f"Account Id from query : {account_id}")
        jwt = get_jwt()
        if not jwt.get("admin"):
            abort(401, message="Only Admin has access to this feature")
        account = Account.query.get_or_404(account_id)
        if account.active == True:
            abort(401, message="Account is already active")
        account.active = True
        try:
            db.session.add(account)
            db.session.commit()
        except SQLAlchemyError as q:
            db.session.rollback()
            abort(400, message=str(q))
        else:
            return {"message": f"Account {account.account_no} reactivated"}, 201

    @cross_origin()
    @jwt_required()
    def delete(self, account_id):
        jwt = get_jwt()
        if not jwt.get("admin"):
            abort(401, message="Only Admin has access to this feature")
        account = Account.query.get_or_404(account_id)
        if account.active == True:
            abort(401, message="Cannot delete active account")
        try:
            db.session.delete(account)
            db.session.commit()
        except SQLAlchemyError as q:
            db.session.rollback()
            abort(400, message=str(q))
        else:
            return {"message": "Account deleted"}, 201
