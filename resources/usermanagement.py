from flask.views import MethodView
from flask_smorest import Blueprint, abort
from CreateTransactionModel import db, AccountHolder
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import UserRegistration, UserLogin
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from redis_connect.redis_connection import blocklist_connection
from datetime import timedelta


blp = Blueprint("AccountHolder", __name__, description="User Management")


@blp.route("/registration")
class Register(MethodView):
    @cross_origin()
    @blp.arguments(UserRegistration)
    @blp.response(201, UserRegistration)
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
    @blp.arguments(UserLogin)
    def post(self, user_data):
        user = AccountHolder.query.filter(
            AccountHolder.email_id == user_data["email_id"].lower()).first()
        if not user:
            abort(404, message="User not found")

        if not (check_password_hash(user.password, user_data["password"])):
            abort(404, message="Incorrect Password")
        access_token = create_access_token(identity=user.user_id)
        return {"access_token": access_token, "admin": user.admin}


@blp.route("/userlogout/<int:user_id>")
class Logout(MethodView):
    @cross_origin()
    @jwt_required()
    def delete(self, user_id):
        if not user_id == get_jwt_identity():
            abort(404, message="User not logged in")
        jti = get_jwt()["jti"]
        blocklist_connection.set(jti, "", ex=timedelta(hours=0.5))
        return {"message": "Access token revoked"}, 201
