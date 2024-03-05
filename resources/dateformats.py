from flask.views import MethodView
from flask_smorest import Blueprint, abort
from CreateTransactionModel import db, DateFormat
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import DateFormatSchema, UploadTransactionsSchema
from flask_cors import cross_origin
from flask import request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask_uploads import UploadSet, DOCUMENTS, UploadNotAllowed
from dateformatupload import uploadDateformat
import os
import json
from dotenv import load_dotenv
load_dotenv()

blp = Blueprint("DateFormats", __name__, description="Date Formats")

docs = UploadSet("statement", DOCUMENTS)


@blp.route("/dateformats")
class DateFormats(MethodView):
    @cross_origin()
    @blp.response(200, DateFormatSchema(many=True))
    def get(self):
        dateformats = DateFormat.query.all()
        return dateformats

    @cross_origin()
    @jwt_required()
    @blp.arguments(DateFormatSchema)
    @blp.response(200, DateFormatSchema)
    def post(self, dateformatdata):
        jwt = get_jwt()
        if not jwt.get("admin"):
            abort(401, message="Only Admin has access to this feature")
        dateformat = DateFormat.query.filter(
            DateFormat.py_date == dateformatdata["py_date"]
        ).first()
        if dateformat:
            abort(409, message="This date format already exists")

        new_dateformat = DateFormat(**dateformatdata)
        percent_count = new_dateformat.py_date.count("%")
        year_count = new_dateformat.py_date.count("Y") + new_dateformat.py_date.count(
            "y"
        )
        month_count = (
            new_dateformat.py_date.count("b")
            + new_dateformat.py_date.count("B")
            + new_dateformat.py_date.count("m")
        )
        day_count = new_dateformat.py_date.count("d") + new_dateformat.py_date.count(
            "D"
        )
        if (
            percent_count != 3
            or year_count != 1
            or month_count != 1
            or day_count != 1
            or not new_dateformat.py_date.startswith("%")
        ):
            abort(405, message="The date is not in correct format")
        try:
            db.session.add(new_dateformat)
            db.session.commit()
        except SQLAlchemyError as q:
            db.session.rollback()
            abort(400, message=str(q))
        else:
            return new_dateformat


@blp.route("/dateformats/<int:date_id>")
class DateFormatOne(MethodView):
    @cross_origin()
    @blp.response(200, DateFormatSchema)
    def get(self, date_id):
        date = DateFormat.query.filter_by(date_id=date_id).first()
        if not date:
            abort(404, message="Date format does not exist")
        return date


@blp.route("/bulkupload-dateformats")
class BulkDateFormats(MethodView):
    @cross_origin()
    @jwt_required()
    def post(self):
        jwt = get_jwt()
        if not jwt.get("admin"):
            abort(401, message="Only Admin has access to this feature")
        date_formats = request.files
        try:
            date_formats_files = docs.save(date_formats["dateformats"])
        except UploadNotAllowed:
            abort(400, message="Upload file in Microsoft Excel format only")
        result = uploadDateformat(date_formats_files)
        os.remove(docs.path(date_formats_files))
        return {"result": result}, 201
