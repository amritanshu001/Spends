from flask.views import MethodView
from flask_smorest import Blueprint, abort
from CreateTransactionModel import db, DateFormat
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import DateFormatSchema
from flask_cors import cross_origin

blp = Blueprint("DateFormats", __name__, description="Date Formats")


@blp.route("/dateformats")
class DateFormats(MethodView):
    @cross_origin()
    @blp.response(200, DateFormatSchema(many=True))
    def get(self):
        dateformats = DateFormat.query.all()
        return dateformats


@blp.route("/dateformats/<int:date_id>")
class DateFormatOne(MethodView):
    @cross_origin()
    @blp.response(200, DateFormatSchema)
    def get(self, date_id):
        date = DateFormat.query.filter_by(date_id=date_id).first()
        if not date:
            abort(404, message="Date format does not exist")
        return date
