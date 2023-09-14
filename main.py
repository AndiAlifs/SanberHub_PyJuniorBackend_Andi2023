from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from database import Base, engine, Session, Account, Transaksi
import random
from datetime import datetime
from schemas import AccountRequest, TransaksiRequest

app = FastAPI()

@app.post("/daftar")
def create_account(account: AccountRequest):
    all_account = Session().query(Account).all()
    for acc in all_account:
        if acc.nik == account.nik:
            return_msg = {
                "remark": "failed - NIK sudah terdaftar"
            }
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=return_msg)
        elif acc.no_hp == account.no_hp:
            return_msg = {
                "remark": "failed - No HP sudah terdaftar"
            }
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=return_msg)

    session = Session(bind=engine, expire_on_commit=False)

    new_account = Account(
        nik=account.nik,
        nama=account.nama,
        no_hp=account.no_hp,
        no_rekening=str(random.randint(100000, 999999)),
    )

    session.add(new_account)
    session.commit()
    session.close()

    return_msg = {
        "remark": "success",
        "data": {
            "no_rekening": new_account.no_rekening,
        }
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=return_msg)

@app.post("/tabung")
def tabung(transaksi: TransaksiRequest):
    session = Session(bind=engine, expire_on_commit=False)
    account = session.query(Account).filter(Account.no_rekening == transaksi.no_rekening).first()

    if account is None:
        return_msg = {
            "remark": "failed - No Rekening tidak ditemukan"
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=return_msg)

    
    account.saldo += transaksi.nominal
    session.commit()

    new_transaksi = Transaksi(
        no_rekening=transaksi.no_rekening,
        nominal=transaksi.nominal,
        waktu="now",
        kode_transaksi="c"
    )
    session.add(new_transaksi)

    session.commit()
    session.close()

    return_msg = {
        "remark": "success",
        "data": {
            "saldo": account.saldo
        }
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=return_msg)

@app.post("/tarik")
def tarik(transaksi: TransaksiRequest):
    session = Session(bind=engine, expire_on_commit=False)
    account = session.query(Account).filter(Account.no_rekening == transaksi.no_rekening).first()

    if account is None:
        return_msg = {
            "remark": "failed - No Rekening tidak ditemukan"
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=return_msg)

    if account.saldo < transaksi.nominal:
        return_msg = {
            "remark": "failed - Saldo tidak cukup"
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=return_msg)

    account.saldo -= transaksi.nominal
    session.commit()

    new_transaksi = Transaksi(
        no_rekening=transaksi.no_rekening,
        nominal=transaksi.nominal,
        waktu="now",
        kode_transaksi="d"
    )

    session.add(new_transaksi)
    session.commit()

    session.close()

    return_msg = {
        "remark": "success",
        "data": {
            "saldo": account.saldo
        }
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=return_msg)

@app.get("/saldo/{no_rekening}")
def get_saldo(no_rekening: str):
    session = Session(bind=engine, expire_on_commit=False)
    account = session.query(Account).filter(Account.no_rekening == no_rekening).first()

    if account is None:
        return_msg = {
            "remark": "failed - No Rekening tidak ditemukan"
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=return_msg)

    return_msg = {
        "remark": "success",
        "data": {
            "saldo": account.saldo
        }
    }
    session.close()
    return JSONResponse(status_code=status.HTTP_200_OK, content=return_msg)

@app.get("/mutasi/{no_rekening}")
def get_mutasi(no_rekening: str):
    session = Session(bind=engine, expire_on_commit=False)
    account = session.query(Account).filter(Account.no_rekening == no_rekening).first()

    if account is None:
        return_msg = {
            "remark": "failed - No Rekening tidak ditemukan"
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=return_msg)

    all_transaksi = session.query(Transaksi).filter(Transaksi.no_rekening == no_rekening).all()
    return_msg = {
        "remark": "success",
        "data": {
            "mutasi": []
        }
    }
    for transaksi in all_transaksi:
        return_msg["data"]["mutasi"].append({
            "waktu": datetime.strftime(transaksi.waktu, '%Y-%m-%d %H:%M:%S'),
            "nominal": transaksi.nominal,
            "kode_transaksi": transaksi.kode_transaksi
        })

    session.close()
    return JSONResponse(status_code=status.HTTP_200_OK, content=return_msg)