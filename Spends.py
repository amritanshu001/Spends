from flask import Flask, render_template, request, g, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy as sql
from datetime import datetime
from CreateTransactionModel import db, BankDetails, Acc_Transaction, Account, AccountHolder, DateFormat
from databaseconnect import get_engine
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
import os
import pandas as pd
from sqlalchemy.exc import IntegrityError
from processfile import processfile
from Forms import LoginForm, DelAccount, DelBankData, BankData, RegisterForm, AddAccount, DelAccount, BankForm, BankList, Upload, SpendsAnalysis, Top5
from flask_uploads import configure_uploads, UploadSet, DOCUMENTS, UploadNotAllowed


app = Flask(__name__)

docs = UploadSet('statement',DOCUMENTS)

app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "Secret"
app.config['SQLALCHEMY_DATABASE_URI'] = get_engine()[0]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_STATEMENT_DEST'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),'temp')
app.config['UPLOADED_STATEMENT_ALLOW'] = ['xls', 'xlsx']

configure_uploads(app,docs)

db.init_app(app)


def get_current_user():
    user_dict = {}
    user_dict['uid'] = None
    user_dict['admin'] = False
    user_dict['name'] = None
    if 'uid' in session:
        user_dict['uid'] = session['uid']
        user_dict['admin'] = session['admin']
        user_dict['name'] = session['name']
    return user_dict

@app.route('/spendanalysis', methods = ['GET','POST'])
def spendanalysis():
    activepage = {}
    activepage['spend'] = True
    cur_user = get_current_user()
    if not cur_user['uid']:
        return(redirect(url_for('login')))
    display = False
    messages = {}
    form = SpendsAnalysis()
    user = AccountHolder.query.filter_by(user_id = cur_user['uid']).first()
    form.select_account.choices = [("0","---")] + [(i.account_id, i.account_no) for i in user.accounts]
    if form.validate_on_submit():
        cur_acc = form.select_account.data
        from_date = form.frm_date.data
        to_date = form.to_date.data

        if from_date > to_date:
            messages['msg_stat'] = "alert-danger"
            messages['shortmsg'] = "Error!"
            messages['longmsg'] = "To Date cannot be greater than from date"
        else:
            txns = Acc_Transaction.query.filter(Acc_Transaction.acc_id == cur_acc, Acc_Transaction.txn_date.between(from_date,to_date))
            if txns.all():
                display = True
                top5cr = txns.filter(Acc_Transaction.withdrawal_amt == 0).order_by(Acc_Transaction.deposit_amt.desc()).limit(5).all()
                top5dr = txns.filter(Acc_Transaction.deposit_amt == 0).order_by(Acc_Transaction.withdrawal_amt.desc()).limit(5).all()
                first_txn = txns.order_by(Acc_Transaction.txn_date).first()
                last_txn = txns.order_by(Acc_Transaction.txn_date.desc()).first()
                credit_summary = txns.with_entities(db.func.sum(Acc_Transaction.deposit_amt).label("Sum"),db.func.count(Acc_Transaction.txn_id).label("Count")).filter(Acc_Transaction.withdrawal_amt == 0).all()
                debit_summary = txns.with_entities(db.func.sum(Acc_Transaction.withdrawal_amt).label("Sum"),db.func.count(Acc_Transaction.txn_id).label("Count")).filter(Acc_Transaction.deposit_amt == 0).all()

                form.incoming.data = credit_summary[0][0]
                form.incoming_txn.data = credit_summary[0][1]
                form.incoming_avg.data = credit_summary[0][0] / credit_summary[0][1]

                form.outgoing.data = debit_summary[0][0]
                form.outgoing_txn.data = debit_summary[0][1]
                form.outgoing_avg.data = debit_summary[0][0] / debit_summary[0][1]

                form.opening_bal.data = first_txn.balance + first_txn.withdrawal_amt - first_txn.deposit_amt
                form.closing_bal.data = last_txn.balance

                if form.closing_bal.data >= form.opening_bal.data:
                    form.balance.data = form.closing_bal.data - form.opening_bal.data
                else:
                    form.balance.data = form.opening_bal.data - form.closing_bal.data

                for ser, txn in enumerate(top5cr,1):
                    txn5 = Top5()
                    txn5.txn_no = ser
                    txn5.txn_date = txn.txn_date
                    txn5.txn_amt = txn.deposit_amt
                    form.top_5_credit.append_entry(txn5)

                for ser, txn in enumerate(top5dr,1):
                    txn5 = Top5()
                    txn5.txn_no = ser
                    txn5.txn_date = txn.txn_date
                    txn5.txn_amt = txn.withdrawal_amt
                    form.top_5_debit.append_entry(txn5)
            else:
                messages['msg_stat'] = "alert-info"
                messages['shortmsg'] = "Information!"
                messages['longmsg'] = "No Values found in database for above search criteria"

    else:
        if request.method == 'POST':
            print ("Before Error Handling: {}".format(display))
            messages['msg_stat'] = "alert-danger"
            messages['shortmsg'] = "Error!"
            messages['longmsg'] = "{}".format(form.errors)

    return render_template("spend.html", activepage = activepage, cur_user = cur_user, form = form, messages = messages, display = display)

@app.route('/login', methods = ['GET','POST'])
def login():
    activepage = {}
    messages = {}
    activepage['login'] = True
    cur_user = get_current_user()
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        user = AccountHolder.query.filter_by(email_id = email).first()
        print(user)
        if user:
            if check_password_hash(user.password, form.password.data):
                session['uid'] = user.user_id
                session['admin'] = user.admin
                session['name'] = user.user_name
                messages['msg_stat'] = "alert-success"
                messages['shortmsg'] = "Success!"
                messages['longmsg'] = "Login Successful"
                return redirect(url_for('manageaccount', **messages))
            else:
                messages['msg_stat'] = "alert-danger"
                messages['shortmsg'] = "Failed!"
                messages['longmsg'] = "Incorrect Password"
        else:
            messages['msg_stat'] = "alert-danger"
            messages['shortmsg'] = "Failed!"
            messages['longmsg'] = "Email {} does not exist in database".format(email)

    return render_template("login.html", activepage = activepage, form = form, cur_user = cur_user, messages = messages)

@app.route('/register', methods = ['GET','POST'])
def register():
    cur_user = get_current_user()
    messages = {}
    activepage = {}
    activepage['register'] = True

    form = RegisterForm()

    if form.validate_on_submit():
        acc_holder  = {}
        acc_holder['user_name'] = form.username.data.lower()
        acc_holder['password'] = generate_password_hash(form.password.data, method = "sha256")
        acc_holder['email_id'] = form.email.data.lower()
        try:
            acc_hldr = AccountHolder(**dict(acc_holder))
            db.session.add(acc_hldr)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            messages['msg_stat'] = "alert-danger"
            messages['shortmsg'] = "Failed!"
            messages['longmsg'] = e.orig.diag.message_detail
        else:
            #acc_hold = AccountHolder.query.filter_by(user_name = acc_holder['user_name'].lower())
            messages['msg_stat'] = "alert-success"
            messages['shortmsg'] = "Success!"
            messages['longmsg'] = "User ID {} created for user {}".format(acc_hldr.user_id,acc_hldr.user_name)            
    return render_template("register.html", activepage = activepage, form = form, messages = messages, cur_user = cur_user)


@app.route('/uploadstatement', methods = ['GET','POST'])
def upload():
    cur_user = get_current_user()
    if not cur_user['uid']:
        return(redirect(url_for('login')))
    activepage = {}
    messages = {}
    activepage['upload'] = True
    user = AccountHolder.query.filter_by(user_id = cur_user['uid']).first()
    form = Upload()
    form.select_account.choices = [("0","---")] + [(i.account_id, i.account_no) for i in user.accounts]

    if form.validate_on_submit():
        if form.select_account.data == 0:
            messages['msg_stat'] = "alert-danger"
            messages['shortmsg'] = "Error!"
            messages['longmsg'] = "Please select Account"
        else:
            try:
                statement_file = docs.save(form.file.data)
            except UploadNotAllowed:
                messages['msg_stat'] = "alert-danger"
                messages['shortmsg'] = "Error!"
                messages['longmsg'] = "Enter file in Microsoft Excel format"
            else:
                selected_acc = Account.query.filter_by(account_id = form.select_account.data).first()
                df = processfile(docs.path(statement_file), selected_acc.bank)
                insert_suc = 0; insert_fail = 0
                for indx, transaction in df.iterrows():
                    acc_txn = Acc_Transaction(**dict(transaction))
                    acc_txn.acc_id = form.select_account.data
                    db.session.add(acc_txn)
                    try:
                        db.session.commit()
                    except IntegrityError as e:
                        db.session.rollback()
                        insert_fail += 1
                        print("Transaction {} already exists. Skipping...".format(transaction['txn_remarks']))
                    else:
                        insert_suc += 1
                messages['msg_stat'] = "alert-info"
                messages['shortmsg'] = "Database Update Status: "
                messages['longmsg'] = "{} records successfully inserted. {} Records failed".format(insert_suc,insert_fail)
                os.remove(docs.path(statement_file))
                
    return render_template("upload.html", activepage = activepage, cur_user = cur_user, form = form, messages = messages)

@app.route('/addbank', methods = ['GET','POST'])
def addbank():
    messages = {}
    activepage = {}
    cur_user = get_current_user()
    if not cur_user['uid']:
        return(redirect(url_for('login')))
    activepage['addbank'] = True
    form = BankForm()
    #form.date_format.choices = [('0','---')]+[(format.date_id, format.date_format) for format in DateFormat.query.all()]
    bankform = BankList()

    if bankform.validate_on_submit() and bankform.refresh.data and bankform.bankname.data != 0:
        bank = BankDetails.query.filter_by(bank_id = bankform.bankname.data).first()
        if bank:
            form = BankForm(obj = bank)

    if form.validate_on_submit() and form.add_bank.data:        
        bank_exists = BankDetails.query.filter_by(bank_name = form.bank_name.data).first()
        if bank_exists:
            form.populate_obj(bank_exists)
            db.session.add(bank_exists)
        else:
            bankdet = BankDetails()
            form.populate_obj(bankdet)
            db.session.add(bankdet)
        try:
            db.session.commit()
        except BaseException as e:
            messages['msg_stat'] = "alert-danger"
            messages['shortmsg'] = "Error!"
            messages['longmsg'] = "{}".format(e) 
        else:
            messages['msg_stat'] = "alert-success"
            messages['shortmsg'] = "Success!"
            if bank_exists:
                messages['longmsg'] = "Bank {} modified in the database".format(bank_exists.bank_name)
            else:
                messages['longmsg'] = "Bank {} added to the database".format(bankdet.bank_name)            
    return render_template("addbank.html", activepage = activepage, cur_user = cur_user, messages = messages, form = form,bankform = bankform)

def validate_account(account_no):
    acc = Account.query.filter_by(account_no = account_no).first()
    if acc:
        exists = True
        if acc.joint:
            joint = True
        else:
            joint = False
    else:
        exists = False
        joint = False
    return [exists, joint, acc]


@app.route('/manageaccount', methods = ['GET','POST'])
def manageaccount():
    cur_user = get_current_user()
    if not cur_user['uid']:
        return(redirect(url_for('login')))
    messages = {}
    delmessages = {}
    activepage = {}
    activepage['addaccount'] = True   
    form = AddAccount()
    acc_hldr = AccountHolder.query.filter_by(user_id = cur_user['uid']).first()
    delform = DelAccount()
    if acc_hldr:
        for account in acc_hldr.accounts:
            if account.active:
                delbnk = DelBankData()
                delbnk.accountno = account.account_no
                banknm = BankDetails.query.filter_by(bank_id = account.bank).first()
                delbnk.bankname = banknm.bank_name   
                delbnk.deactivate = False
                delform.bank_det.append_entry(delbnk)

    if delform.del_acc.data and delform.validate_on_submit():
        print(delform.del_acc)
        d = 0
        for account in delform.bank_det:
            print ("Processing Account {}".format(account.accountno.data))
            if account.deactivate.data:
                d = 1
                delacc = Account.query.filter_by(account_no = account.accountno.data).first()
                delacc.active = False
                try:
                    db.session.add(delacc)
                    db.session.commit()
                except BaseException as b:
                    db.session.rollback()
                    delmessages['msg_stat'] = "alert-danger"
                    delmessages['shortmsg'] = "Failed!"
                    delmessages['longmsg'] = "Database error occured.!"
                    print(b)
                else:
                    delmessages['msg_stat'] = "alert-success"
                    delmessages['shortmsg'] = "Success!"
                    delmessages['longmsg'] = "Account {} deactivated!".format(account.accountno.data)

        if d == 0:
            delmessages['msg_stat'] = "alert-danger"
            delmessages['shortmsg'] = "Error!"
            delmessages['longmsg'] = "Select Atleast 1 Account for deactivation"

    if form.add_acc.data and form.validate_on_submit():
        print(form.add_acc)
        f = 0
        for bank in form.banks:
            if bank.bankname.data != 0:
                f = 1
                if bank.accountno.data:
                    acc = Account()
                    [acc_exist, acc_joint, exist_acc] = validate_account(bank.accountno.data)
                    if acc_exist:
                        if acc_joint:
                            x = 0
                            for user in exist_acc.users:
                                if user.user_id == cur_user['uid']:
                                    x =1 
                                    break
                            if x ==1:
                                messages['msg_stat'] = "alert-info"
                                messages['shortmsg'] = "Info!"
                                messages['longmsg'] = "Account {} already exists for current user. Skipping...".format(bank.accountno.data)
                            else:
                                exist_acc.users.append(acc_hldr)
                                db.session.add(exist_acc)
                        else:
                            messages['msg_stat'] = "alert-danger"
                            messages['shortmsg'] = "Error!"
                            messages['longmsg'] = "Account {} already assigned to another user!".format(bank.accountno.data)
                    else:
                        acc.account_no = bank.accountno.data
                        acc.bank = bank.bankname.data
                        acc.joint = bank.jointacc.data
                        acc.users.append(acc_hldr)
                        db.session.add(acc)
                        #print(db.session.new, db.session.dirty, db.session.deleted)
                        try:
                            db.session.commit()
                        except BaseException as e:
                            db.session.rollback()
                            messages['msg_stat'] = "alert-danger"
                            messages['shortmsg'] = "Failed!"
                            messages['longmsg'] = "Accounts Not Added!"
                            print (e)
                        else:
                            messages['msg_stat'] = "alert-success"
                            messages['shortmsg'] = "Success!"
                            messages['longmsg'] = "Accounts Added to user id {}".format(cur_user['uid'])        
                else:
                    messages['msg_stat'] = "alert-danger"
                    messages['shortmsg'] = "Error!"
                    messages['longmsg'] = "Account Cannot be blank"
        if f ==0:
            messages['msg_stat'] = "alert-danger"
            messages['shortmsg'] = "Error!"
            messages['longmsg'] = "Enter Atleast 1 Bank and Account Combination"            


    return render_template("addaccount.html", activepage = activepage, form = form, messages = messages, cur_user = cur_user, delform = delform, delmessages = delmessages)

@app.route('/logout')
def logout():
    session.pop('uid', None)
    session.pop('admin', None)
    session.pop('name', None)
    return redirect(url_for('login'))
    

if __name__ == '__main__':
    app.run()

