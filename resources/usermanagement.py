from flask.views import MethodView
from flask_smorest import Blueprint, abort
from CreateTransactionModel import db, AccountHolder
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import AccountHolderSchema
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash

blp = Blueprint("AccountHolder", __name__, description="User Management")


@blp.route("/registration")
class Register(MethodView):
    @cross_origin()
    @blp.arguments(AccountHolderSchema)
    @blp.response(201, AccountHolderSchema)
    def post(self, user_data):
        print(user_data)
        user = AccountHolder(**user_data)

        user.password = generate_password_hash(
            user_data["password"], method="sha256")

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError as err:
            db.session.rollback()
            # return {"msg": str(err)}
            abort(404, message=str(err))
        else:
            return user
