from flask.views import MethodView
from flask_smorest import Blueprint, abort
from CreateTransactionModel import db, AccountHolder
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import AccountHolderSchema
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity

blp = Blueprint("AccountHolder", __name__, description="User Management")


@blp.route("/registration")
class Register(MethodView):
    @cross_origin()
    @blp.arguments(AccountHolderSchema)
    @blp.response(201, AccountHolderSchema)
    def post(self, user_data):
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


@blp.route("/userlogin")
class Login(MethodView):
    @cross_origin()
    @blp.arguments(AccountHolderSchema)
    def get(self, user_data):
        user = AccountHolder.query.filter(
            AccountHolder.email_id == user_data["email_id"]).first()
        if not user:
            abort(404, message="User not found")

        if not (check_password_hash(user.password, user_data["password"])):
            abort(404, message="Incorrect Password")
        access_token = create_access_token(identity=user.user_id)
        return {"access_token": access_token}
