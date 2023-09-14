from fastapi import FastAPI
from database import Base, engine, Session, Account, Transaksi
import random
from schemas import AccountRequest, TransaksiRequest

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/daftar")
def create_account(account: AccountRequest):

    all_account = Session().query(Account).all()
    for acc in all_account:
        if acc.nik == account.nik:
            return {
                "remark": "failed",
                "data": {
                    "reason": "NIK sudah terdaftar"
                }
            }
        elif acc.no_hp == account.no_hp:
            return {
                "remark": "failed",
                "data": {
                    "reason": "No HP sudah terdaftar"
                }
            }

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

    return {
        "remark": "success",
        "data": {
            "no_rek": new_account.no_rek,
        }
    }
