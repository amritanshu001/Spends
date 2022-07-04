from CreateTransactionModel import DateFormat, db
import pandas as pd

df = pd.read_excel('Dateformats.xlsx')

for indx, format in df.iterrows():
    db.session.add(DateFormat(**dict(format)))
    db.session.commit()