# import fastapi yang merupakan backend app
from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse

# import database yang merupakan model dan akses database
from database.model import Base, engine, Session, Account, Transaksi

# import schemas yang merupakan request dan response
from database.schemas import AccountRequest, TransaksiRequest

# import package yang digunakan dalam logic
from datetime import datetime
import random

def get_all_account(session):
    all_account = session.query(Account).all()
    return all_account

def account_by_no_rekening(session, no_rekening):
    account = session.query(Account).filter(Account.no_rekening == no_rekening).first()
    return account

def get_accounts_by_name(session, nama):
    accounts = session.query(Account).filter(Account.nama.like('%{nama}%')).all()
    return accounts

def create_account(session, NewAccount: Account):
    session.add(NewAccount)
    return NewAccount

def tambah_saldo(session, no_rekening, jumlah):
    account = session.query(Account).filter(Account.no_rekening == no_rekening).first()
    account.saldo += jumlah
    return account

def tarik_saldo(session, no_rekening, jumlah):
    account = session.query(Account).filter(Account.no_rekening == no_rekening).first()
    account.saldo -= jumlah
    return account

def create_transaksi(session, new_transaksi: Transaksi):
    session.add(new_transaksi)
    return new_transaksi