import pandas as pd
from CreateTransactionModel import Account, BankDetails, Acc_Transaction, AccountHolder
import os
import win32com.client as win32


#def processfile():
def processfile(path, bankid):
    excel = win32.gencache.EnsureDispatch('Excel.Application')
    excel.Visible = False
    #fil_path = r"D:\amritanshu\OneDrive - Infosys Limited\Bank Statement analysis\PreviousYearStatements"
    #file_name = r"055201001092.xlsx"
    #comment this when path is passed from Sepnds.py
    #path = os.path.join(fil_path,file_name)

    wb = excel.Workbooks.Open(path)

    #bankid = 1
    bank_dets = BankDetails.query.filter_by(bank_id = bankid).first()

    sht_last_row = {}
    total_rows = 0
    for sht in wb.Sheets:
        lastrow = sht.Cells(bank_dets.start_row,bank_dets.val_date_col).End(4)
        sht_last_row[sht.Name] = lastrow.Row
    wb.Close()
        
    extract_cols = [bank_dets.val_date_col-1, bank_dets.txn_date_col-1,
                    bank_dets.chq_no_col-1, bank_dets.txn_rmrk_col-1,
                    bank_dets.with_amt_col-1, bank_dets.crdt_amt_col-1,
                    bank_dets.bal_col-1]
    col_names = ['val_date_col', 'txn_date_col',
                    'chq_no_col', 'txn_rmrk_col',
                    'with_amt_col', 'crdt_amt_col',
                    'bal_col']
    final_df = pd.DataFrame(columns=col_names)
    sheets = pd.ExcelFile(path)
    for sheet in sheets.sheet_names:
        no_rows = sht_last_row[sheet] - bank_dets.start_row
        df = pd.read_excel(path, sheet_name=sheet, usecols=extract_cols, skiprows=bank_dets.start_row-1, names=col_names, nrows=no_rows)
        final_df = final_df.append(df)

    return(final_df)

    
