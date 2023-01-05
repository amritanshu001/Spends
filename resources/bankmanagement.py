from flask.views import MethodView
from flask_smorest import Blueprint, abort
from CreateTransactionModel import db, BankDetails, AccountHolder
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import BanksSchema
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

blp = Blueprint("Bank Management", __name__, description="List of Banks")


@blp.route("/banks")
class Banks(MethodView):
    @cross_origin()
    @jwt_required()
    @blp.response(200, BanksSchema(many=True))
    def get(self):
        # jwt = get_jwt()
        # if not jwt.get("admin"):
        #     abort(401, message="Only Admin has access to this feature")
        banks = BankDetails.query.order_by(BankDetails.bank_id).all()

        return banks

    @cross_origin()
    @jwt_required()
    @blp.arguments(BanksSchema)
    @blp.response(201, BanksSchema)
    def post(self, bank_data):
        jwt = get_jwt()
        if not jwt.get("admin"):
            abort(401, message="Only Admin has access to this feature")

        bank = BankDetails(**bank_data)

        try:
            db.session.add(bank)
            db.session.commit()
        except IntegrityError as i:
            db.session.rollback()
            abort(409, message="The Bank already exists!")
        except SQLAlchemyError as q:
            db.session.rollback()
            abort(409, message=str(q))
        else:
            return bank


@blp.route("/banks/<int:bank_id>")
class Bank(MethodView):
    @cross_origin()
    @jwt_required()
    @blp.response(200, BanksSchema)
    def get(self, bank_id):
        jwt = get_jwt()
        if not jwt.get("admin"):
            abort(401, message="Only Admin has access to this feature")
        bank = BankDetails.query.get_or_404(bank_id)
        print(bank)
        return bank

    @cross_origin()
    @jwt_required()
    def delete(self, bank_id):
        jwt = get_jwt()
        if not jwt.get("admin"):
            abort(401, message="Only Admin has access to this feature")
        bank = BankDetails.query.get_or_404(bank_id)

        account_exists = bank.accounts.first()
        if account_exists:
            abort(403, message="This bank has accounts assigned. Delete all accounts of this bank before deleting the bank")

        try:
            db.session.delete(bank)
            db.session.commit()
        except SQLAlchemyError as q:
            db.session.rollback()
            abort(422, message=str(q))
        else:
            return {"message": "Bank Deleted"}, 200

    @cross_origin()
    @jwt_required()
    @blp.arguments(BanksSchema)
    @blp.response(200, BanksSchema)
    def put(self, bank_data, bank_id):
        jwt = get_jwt()
        if not jwt.get("admin"):
            abort(401, message="Only Admin has access to this feature")
        bank = BankDetails.query.get(bank_id)
        if not bank:
            new_bank = BankDetails(**bank_data)
            try:
                db.session.add(new_bank)
                db.session.commit()
            except SQLAlchemyError as q:
                db.session.rollback()
                abort(422, message=str(q))
            else:
                return new_bank
        bank = BankDetails(**bank_data, bank_id=bank_id)
        print(bank)
        try:
            db.session.merge(bank)
            db.session.commit()
        except SQLAlchemyError as q:
            db.session.rollback()
            abort(422, message=str(q))
        else:
            return bank
