# pylint: disable=E1101
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from CreateTransactionModel import db, AccountHolder
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import UserRegistration, UserLogin, PasswordReset, PasswordResetRequest
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
    verify_jwt_in_request,
)
from redis_connect.redis_connection import blocklist_connection
from datetime import timedelta
from config import config
from redis.exceptions import ConnectionError
import platform
import os

# from flask_mail import Message, Mail
from flask import render_template

# from utils import mail
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SendGridMail
import datetime

if platform.system() == "Linux":
    try:
        token_timeout = int(os.getenv("TOKEN_TIMEOUT_HOURS"))
        refresh_token_timeout = int(os.getenv("REFRESH_TOKEN_TIMEOUT_DAYS"))
    except:
        token_timeout = 1
        refresh_token_timeout = 1
else:
    token_timeout = config(section="token-timeout")["fresh-token-hrs"]
    refresh_token_timeout = config(section="token-timeout")["refresh-token-days"]
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

        user.password = generate_password_hash(user_data["password"], method="sha256")

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as i:
            db.session.rollback()
            abort(403, message="User Already Registered")
        except SQLAlchemyError as err:
            db.session.rollback()
            # return {"msg": str(err)}
            abort(403, message=str(err))
        else:
            return user


@blp.route("/userlogin")
class Login(MethodView):
    @cross_origin()
    @blp.arguments(UserLogin)
    def post(self, user_data):
        user = AccountHolder.query.filter(
            AccountHolder.email_id == user_data["email_id"].lower()
        ).first()
        if not user:
            abort(404, message="User not found")

        if not (check_password_hash(user.password, user_data["password"])):
            abort(404, message="Incorrect Password")
        access_token = create_access_token(identity=user.user_id)

        return {
            "access_token": access_token,
            "admin": user.admin,
            "expires_in": token_timeout * 3600,
            "email_id": user.email_id,
        }


@blp.route("/userlogout")
class Logout(MethodView):
    @cross_origin()
    def delete(self):
        if not verify_jwt_in_request():
            abort(404, message="Missing JWT")
        user_id = get_jwt_identity()
        user = AccountHolder.query.get_or_404(user_id)
        jti = get_jwt()["jti"]
        try:
            blocklist_connection.set(
                jti, platform.system(), ex=timedelta(hours=token_timeout)
            )
        except ConnectionError as c:
            abort(404, message=str(c))
        return {"message": "User Logged Out", "ok": True}, 201


@blp.route("/pwd-reset-request")
class PwdReset(MethodView):
    @cross_origin()
    @blp.arguments(PasswordResetRequest)
    @blp.response(201, PasswordResetRequest)
    def post(self, email_data):
        user = AccountHolder.query.filter(
            AccountHolder.email_id == email_data["email_id"].lower()
        ).first()
        if not user:
            abort(404, message="User not found")
        import uuid

        hash = uuid.uuid4().hex
        user.reset_hash = hash
        user.reset_expiry = datetime.datetime.now() + datetime.timedelta(
            seconds=24 * 60 * 60
        )
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError as err:
            db.session.rollback()
            abort(403, message=str(err))
        reset_link = email_data["site_url"] + "/" + hash
        msg = SendGridMail(
            subject="Request for Password reset: {}".format(user.user_name),
            to_emails=email_data["email_id"],
            from_email=os.environ.get("MAIL_USERNAME"),
            html_content=render_template(
                "password_reset.html", email_id=user.email_id, reset_link=reset_link
            ),
        )
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        try:
            response = sg.send(msg)
            print(response.status_code)
            print(response.body)
            print(response.headers)
            return {"email_id": email_data["email_id"], "userHash": hash}
        except Exception as e:
            print(e)
            abort(500, message=str(e))

    @cross_origin()
    @blp.arguments(PasswordReset)
    @blp.response(201, PasswordReset)
    def put(self, user_data):
        user = AccountHolder.query.filter(
            AccountHolder.reset_hash == user_data["userHash"]
        ).first_or_404()
        if not user:
            abort(404, message="User not found")
        if user.reset_hash == None:
            abort(400, message="Password Reset has not been requested for this user")
        if user.reset_hash != user_data["userHash"]:
            abort(401, message="Hash does not match the user")
        if user.reset_expiry < datetime.datetime.now():
            user.reset_hash = None
            user.reset_expiry = None
            try:
                db.session.add(user)
                db.session.commit()
            except SQLAlchemyError as err:
                db.session.rollback()
                abort(403, message=str(err))
            else:
                abort(410, message="Reset Link has expired, send a new reset request")
        user.password = generate_password_hash(
            user_data["newPassword"], method="sha256"
        )
        user.reset_hash = None
        user.reset_expiry = None
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError as err:
            db.session.rollback()
            abort(403, message=str(err))
        return {"email_id": user.email_id}
