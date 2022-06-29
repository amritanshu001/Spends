from flask import Flask, render_template, request, g, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy as sql
from datetime import datetime
from CreateTransactionModel import db, BankDetails, Acc_Transaction, Account, AccountHolder
from databaseconnect import get_engine
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField, EmailField, SelectField, Form, FormField, FieldList, BooleanField, SubmitField
from wtforms.validators import InputRequired, Length, Email
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "Secret"
app.config['SQLALCHEMY_DATABASE_URI'] = get_engine()[0]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

class LoginForm(FlaskForm):
    email = EmailField("Email Id", validators=[InputRequired(message = "Email cannot be blank"),
            Length(min= 8, max= 200)
    ])
    password = PasswordField("Password", validators=[InputRequired(message = "Password cannot be blank"),
            Length(min= 8, max= 50)
    ])

class DelBankData(Form):
    bankname = StringField("Bank", render_kw = {'readonly':True})
    accountno = StringField("Account No.", render_kw = {'readonly':True})
    deactivate = BooleanField("Deactivate")

class BankData(Form):
    bankname = SelectField("Bank",coerce=int, choices=[("0","---")] + [(bank.bank_id, bank.bank_name) for bank in BankDetails.query.all()])
    accountno = StringField("Account No.",validators=[
        Length(max = 20)
    ])
    jointacc = BooleanField("Joint")

class RegisterForm(FlaskForm):
    username = StringField("User Name", validators=[InputRequired(message = "User Name cannot be blank"),
            Length(min = 8, max= 200)
    ])
    password = PasswordField("Password", validators=[InputRequired(message = "Password cannot be blank"),
            Length(min= 8, max= 50)
    ])
    email = EmailField("Email Id", validators=[InputRequired(message = "Email cannot be blank"),
            Length(min= 8, max= 200)
    ])

class AddAccount(FlaskForm):
    banks = FieldList(FormField(BankData),min_entries=3)
    add_acc = SubmitField("Add Accounts")

class DelAccount(FlaskForm):
    bank_det = FieldList(FormField(DelBankData), min_entries=0)
    del_acc = SubmitField("Delete Accounts") 

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
    cur_user = get_current_user()
    if not cur_user['uid']:
        return(redirect(url_for('login')))
    activepage = {}
    activepage['spend'] = True
    return render_template("home.html", activepage = activepage, cur_user = cur_user)

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
        if user:
            if check_password_hash(user.password, form.password.data):
                session['uid'] = user.user_id
                session['admin'] = user.admin
                session['name'] = user.user_name
                return redirect(url_for('spendanalysis'))
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
    activepage['upload'] = True
    return render_template("register.html", activepage = activepage, cur_user = cur_user)

@app.route('/addbank', methods = ['GET','POST'])
def addbank():
    cur_user = get_current_user()
    if not cur_user['uid']:
        return(redirect(url_for('login')))
    activepage = {}
    activepage['addbank'] = True
    return render_template("register.html", activepage = activepage, cur_user = cur_user)

def validate_account(account_no):
    acc = Account.query.filter_by(account_no = account_no).first()
    if acc:
        exists = True
        if acc.joint:
            joint = True
            users = acc.users
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
    print ("Before processing: {}".format(delform))
    if acc_hldr:
        for account in acc_hldr.accounts:
            if account.active:
                delbnk = DelBankData()
                delbnk.accountno = account.account_no
                banknm = BankDetails.query.filter_by(bank_id = account.bank).first()
                delbnk.bankname = banknm.bank_name   
                delbnk.deactivate = False
                delform.bank_det.append_entry(delbnk)
    print ("After Processing: {}".format(delform))

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

