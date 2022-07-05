from CreateTransactionModel import DateFormat, db
import pandas as pd
from sqlalchemy.exc import IntegrityError
import os

cur_path = os.path.dirname(os.path.realpath(__file__))

os.chdir(cur_path)

df = pd.read_excel('Dateformats.xlsx')

for indx, format in df.iterrows():
    db.session.add(DateFormat(**dict(format)))
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        print ("Format {} already exists. Skipping...".format(format.date_format))
    else:
        print ("Format {} added successfully".format(format.date_format))