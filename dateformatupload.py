from CreateTransactionModel import DateFormat, db
import pandas as pd
from sqlalchemy.exc import IntegrityError
import os


def uploadDateformat(file_name):
    # cur_path = os.path.dirname(os.path.realpath(__file__))

    # os.chdir(cur_path)

    df = pd.read_excel(file_name, engine="openpyxl")
    result = []
    for indx, format in df.iterrows():
        db.session.add(DateFormat(**dict(format)))
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            result.append(
                {
                    format.date_format: "Format {} already exists. Skipping...".format(
                        format.date_format
                    )
                }
            )
        else:
            result.append(
                {
                    format.date_format: "Format {} added successfully".format(
                        format.date_format
                    )
                }
            )
    return result
