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
            DateFormat.date_format == dateformatdata["date_format"]
        ).first()
        if dateformat:
            abort(409, message="This date format already exists")
        try:
            db.session.add(dateformat)
            db.session.commit()
        except SQLAlchemyError as q:
            db.session.rollback()
            abort(400, message=str(q))
        else:
            return dateformat


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
