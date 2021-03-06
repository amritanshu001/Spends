import pandas as pd
from CreateTransactionModel import Account, BankDetails, Acc_Transaction, AccountHolder, DateFormat
import os
import xlrd
import openpyxl as xl
import pathlib

def processfile(path, bankid):

    extension = pathlib.Path(path).suffix
    if extension == '.xlsx':
        engine = 'openpyxl'
    elif extension == '.xls':
        engine = 'xlrd'

    bank_dets = BankDetails.query.filter_by(bank_id = bankid).first()
    sht_last_row = {}

    if engine == 'openpyxl':
        wb = xl.load_workbook(path, read_only=True)
        for sheet in wb:
            f=0
            for row in sheet.iter_rows(min_row = bank_dets.start_row+1, min_col = bank_dets.val_date_col, max_col = bank_dets.val_date_col):
                for cell in row:
                    if cell.value == None or cell.value == "":
                        if sheet.cell(cell.row+1,bank_dets.val_date_col).value == None or sheet.cell(cell.row+1,bank_dets.val_date_col).value == "":
                            sht_last_row[sheet.title] = cell.row-1
                            f=1
                            break
                if f == 1:
                    break
        wb.close()
    elif engine == 'xlrd':
        wb = xlrd.open_workbook(path)
        for sheet_name in wb.sheet_names():
            sht = wb.sheet_by_name(sheet_name)
            f = 0
            for row in range(bank_dets.start_row, sht.nrows):
                for col in range(bank_dets.val_date_col, bank_dets.val_date_col+1):
                    if sht.cell(row,col-1).value == None or sht.cell(row,col-1).value == "":
                        if sht.cell(row+1,col-1).value == None or sht.cell(row+1,col-1).value == "":
                            f=1
                            sht_last_row[sheet_name] = row
                            break
                if f == 1:
                    break

        
    extract_cols = [bank_dets.val_date_col-1, bank_dets.txn_date_col-1,
                    bank_dets.chq_no_col-1, bank_dets.txn_rmrk_col-1,
                    bank_dets.with_amt_col-1, bank_dets.crdt_amt_col-1,
                    bank_dets.bal_col-1]
    col_names = ['value_date', 'txn_date',
                    'cheque_no', 'txn_remarks',
                    'withdrawal_amt', 'deposit_amt',
                    'balance']
    final_df = pd.DataFrame(columns=col_names)
    sheets = pd.ExcelFile(path, engine=engine)
    for sheet in sheets.sheet_names:
        no_rows = sht_last_row[sheet] - bank_dets.start_row
        df = pd.read_excel(path, sheet_name=sheet, usecols=extract_cols, skiprows=bank_dets.start_row-1, names=col_names, nrows=no_rows)
        final_df = pd.concat([final_df, df])

    py_format = DateFormat.query.filter_by(date_id = bank_dets.date_id).first()

    final_df['value_date'] = pd.to_datetime(final_df['value_date'],format=py_format.py_date)
    final_df['txn_date'] = pd.to_datetime(final_df['txn_date'],format=py_format.py_date)
    final_df['withdrawal_amt'] = pd.to_numeric(final_df['withdrawal_amt'])
    final_df['deposit_amt'] = pd.to_numeric(final_df['deposit_amt'])
    final_df['balance'] = pd.to_numeric(final_df['balance'])

    return(final_df.dropna(subset = 'txn_date'))

    
