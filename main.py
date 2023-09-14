from fastapi import FastAPI
from database import Base, engine, Session, Account, Transaksi
import random
from schemas import AccountRequest, TransaksiRequest

app = FastAPI()

def check_account(no_rek):
    session = Session(bind=engine, expire_on_commit=False)
    account = session.query(Account).filter_by(no_rek=no_rek).first()
    session.close()
    return account

@app.post("/tabung")
def tabung(transaksi: TransaksiRequest):
    account = check_account(transaksi.no_rek)
    
    if account is None:
        return_msg = {
            "remark": "failed",
            "data": {
                "reason": "No Rekening tidak ditemukan"
            }
        }
        return json_response(status_code=400, content=return_msg)

    session = Session(bind=engine, expire_on_commit=False)
    account.saldo += transaksi.nominal
    session.commit()
    session.close()

    return_msg = {
        "remark": "success",
        "data": {
            "saldo": account.saldo
        }
    }
    return json_response(status_code=200, content=return_msg)


@app.post("/daftar")
def create_account(account: AccountRequest):
    all_account = Session().query(Account).all()
    for acc in all_account:
        if acc.nik == account.nik:
            return_msg = {
                "remark": "failed",
                "data": {
                    "reason": "NIK sudah terdaftar"
                }
            }
            return json_response(status_code=400, content=return_msg)
        elif acc.no_hp == account.no_hp:
            return_msg = {
                "remark": "failed",
                "data": {
                    "reason": "No HP sudah terdaftar"
                }
            }
            return json_response(status_code=400, content=return_msg)

    session = Session(bind=engine, expire_on_commit=False)

    new_account = Account(
        nik=account.nik,
        nama=account.nama,
        no_hp=account.no_hp,
        no_rek=str(random.randint(100000, 999999)),
    )

    session.add(new_account)
    session.commit()
    session.close()

    return_msg = {
        "remark": "success",
        "data": {
            "no_rek": new_account.no_rek,
        }
    }
    return json_response(status_code=200, content=return_msg)
