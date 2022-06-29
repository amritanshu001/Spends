from CreateTransactionModel import db, BankDetails
import pandas as pd
import os

file_path = r"D:\amritanshu\OneDrive - Infosys Limited\Bank Statement analysis\PreviousYearStatements"
file_name = r"bank details.xlsx"

df = pd.read_excel(os.path.join(file_path,file_name))

for idx, bank in df.iterrows():
    db.session.add(BankDetails(**dict(bank)))
    db.session.commit() 