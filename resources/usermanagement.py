from flask.views import MethodView
from flask_smorest import Blueprint, abort
from CreateTransactionModel import db, AccountHolder
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import UserRegistration, UserLogin
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request
from redis_connect.redis_connection import blocklist_connection
from datetime import timedelta
from config import config
import platform
import os

if platform.system() == 'Linux':
    try:
        token_timeout = os.getenv("TOKEN_TIMEOUT_HOURS")
        refresh_token_timeout = os.getenv("REFRESH_TOKEN_TIMEOUT_DAYS")
    except:
        token_timeout = 1
        refresh_token_timeout = 1
else:
    token_timeout = config(section="token-timeout")["fresh-token-hrs"]
    refresh_token_timeout = config(
        section="token-timeout")["refresh-token-days"]
    try:
        token_timeout = int(token_timeout)
        refresh_token_timeout = int(refresh_token_timeout)
    except:
        token_timeout = 1
        refresh_token_timeout = 1


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

        return {"access_token": access_token, "admin": user.admin, "expires_in": token_timeout*3600}


@blp.route("/userlogout")
class Logout(MethodView):
    @cross_origin()
    def delete(self):
        if not verify_jwt_in_request():
            abort(404, message="Missing JWT")
        user_id = get_jwt_identity()
        user = AccountHolder.query.get_or_404(user_id)
        jti = get_jwt()["jti"]
        blocklist_connection.set(jti, "", ex=timedelta(hours=0.5))
        return {"message": "User Logged Out", "ok": True}, 201
