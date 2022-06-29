DROP TABLE IF EXISTS bank_details;

CREATE TABLE IF NOT EXISTS bank_details
(
    bank_id serial primary key,
    bank_name varchar(200) NOT NULL,
    val_date_col integer not null,
    txn_date_col integer not null,
    chq_no_col integer not null,
    txn_rmrk_col integer not null,
    with_amt_col integer not null,
    crdt_amt_col integer not null,
    bal_col integer not null,

    CONSTRAINT "unique_bankname" UNIQUE (bank_name)
)

TABLESPACE pg_default;
ALTER TABLE IF EXISTS bank_details
    OWNER to "Amritanshu";

DROP TABLE IF EXISTS accountholder;

CREATE TABLE IF NOT EXISTS accountholder
(
    user_id serial primary key not NULL,
    user_name varchar(200) NOT NULL,
    email_id varchar(200) NOT NULL,
    password varchar(50) NOT NULL,
    u_active boolean default True,
    admin boolean default False,

    CONSTRAINT "unique_email" UNIQUE (email_id)
)

TABLESPACE pg_default;
ALTER TABLE IF EXISTS accountholder
    OWNER to "Amritanshu";

DROP TABLE IF EXISTS account;
CREATE TABLE IF NOT EXISTS account
(
    account_id serial primary key not NULL,
    account_no varchar(20) NOT NULL,
    active boolean default True,
    joint boolean default False,
    bank integer not null, 

    CONSTRAINT "accountno" UNIQUE (account_no),
    CONSTRAINT "bank_fkey" 
        FOREIGN KEY (bank)
            REFERENCES bank_details(bank_id)
)

TABLESPACE pg_default;
ALTER TABLE IF EXISTS account
    OWNER to "Amritanshu";

DROP TABLE IF EXISTS acc_transaction;
CREATE TABLE IF NOT EXISTS acc_transaction
(
    txn_id serial primary key not NULL,
    value_date date not null,
    txn_date date not null,
    txn_remarks text not null, 
    cheque_no varchar(20), 
    withdrawal_amt float8,
    deposit_amt float8,
    balance float8 not null,
    acc_id integer not null,

    CONSTRAINT "acc_pkey" 
        FOREIGN KEY(acc_id)
            REFERENCES account(account_id)

)

TABLESPACE pg_default;
ALTER TABLE IF EXISTS acc_transaction
    OWNER to "Amritanshu";

DROP TABLE IF EXISTS bank_users;
create table bank_users(
	bank_id Integer not null, 
	user_id Integer not null, 
	Constraint "b_prime" primary key (bank_id,user_id),
	CONSTRAINT "user_fkey2" 
        FOREIGN KEY(user_id)
            REFERENCES accountholder(user_id),
	CONSTRAINT "bank_fkey2" 
        FOREIGN KEY(bank_id)
            REFERENCES bank_details(bank_id)
	
)
TABLESPACE pg_default;
ALTER TABLE IF EXISTS bank_users
    OWNER to "Amritanshu";


DROP TABLE IF EXISTS account_users;
create table account_users(
	account_id Integer not null, 
	user_id Integer not null, 
	Constraint "b_prime" primary key (bank_id,user_id),
	CONSTRAINT "user_fkey3" 
        FOREIGN KEY(user_id)
            REFERENCES accountholder(user_id),
	CONSTRAINT "account_fkey2" 
        FOREIGN KEY(account_id)
            REFERENCES account(account_id)
	
)
TABLESPACE pg_default;
ALTER TABLE IF EXISTS account_users
    OWNER to "Amritanshu";