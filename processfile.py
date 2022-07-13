import pandas as pd
from CreateTransactionModel import Account, BankDetails, Acc_Transaction, AccountHolder, DateFormat
import os
import xlrd
import openpyxl as xl
#import win32com.client as win32
#import pythoncom

def processfile(path, bankid):
    #pythoncom.CoInitialize()
    #excel = win32.gencache.EnsureDispatch('Excel.Application')
    #excel.Visible = False

    bank_dets = BankDetails.query.filter_by(bank_id = bankid).first()
    sht_last_row = {}

    wb = xl.load_workbook(path, read_only=True)
    for sheet in wb:
        f=0
        for row in sheet.iter_rows(min_row = bank_dets.start_row+1, min_col = bank_dets.val_date_col, max_col = bank_dets.val_date_col):
            for cell in row:
                if cell.value == None or cell.value == "":
                    sht_last_row[sheet.title] = cell.row-1
                    f=1
                    break
            if f == 1:
                break
    wb.close()
        
    extract_cols = [bank_dets.val_date_col-1, bank_dets.txn_date_col-1,
                    bank_dets.chq_no_col-1, bank_dets.txn_rmrk_col-1,
                    bank_dets.with_amt_col-1, bank_dets.crdt_amt_col-1,
                    bank_dets.bal_col-1]
    col_names = ['value_date', 'txn_date',
                    'cheque_no', 'txn_remarks',
                    'withdrawal_amt', 'deposit_amt',
                    'balance']
    final_df = pd.DataFrame(columns=col_names)
    sheets = pd.ExcelFile(path, engine='openpyxl')
    for sheet in sheets.sheet_names:
        no_rows = sht_last_row[sheet] - bank_dets.start_row
        df = pd.read_excel(path, sheet_name=sheet, usecols=extract_cols, skiprows=bank_dets.start_row-1, names=col_names, nrows=no_rows)
        final_df = pd.concat([final_df, df])
        #final_df = final_df.append(df)

    py_format = DateFormat.query.filter_by(date_id = bank_dets.date_id).first()
    
    final_df['value_date'] = pd.to_datetime(final_df['value_date'],format=py_format.py_date)
    final_df['txn_date'] = pd.to_datetime(final_df['txn_date'],format=py_format.py_date)
    final_df['withdrawal_amt'] = pd.to_numeric(final_df['withdrawal_amt'])
    final_df['deposit_amt'] = pd.to_numeric(final_df['deposit_amt'])
    final_df['balance'] = pd.to_numeric(final_df['balance'])

    return(final_df)

    
