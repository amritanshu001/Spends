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
        jwt = get_jwt()
        if not jwt.get("admin"):
            abort(401, "Only Admin has access to this feature")
        banks = BankDetails.query.all()
        return banks

    @cross_origin()
    @jwt_required()
    @blp.arguments(BanksSchema)
    @blp.response(201, BanksSchema)
    def post(self, bank_data):
        jwt = get_jwt()
        if not jwt.get("admin"):
            abort(401, "Only Admin has access to this feature")

        bank = BankDetails(**bank_data)

        try:
            db.session.add(bank)
            db.session.commit()
        except IntegrityError as i:

            db.session.rollback()
            print(dir(i._message))
            abort(404, message=str(i))
        except SQLAlchemyError as q:
            db.session.rollback()
            print(dir(q))
            abort(404, message=str(q))
        else:
            return bank
