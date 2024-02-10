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

app = FastAPI() # inisialisasi app

# function untuk mendapatkan session
def get_session():
    session = Session(bind=engine, expire_on_commit=False)
    return session
    
# function untuk menutup session
def close_session(session):
    session.commit()
    session.close()

# endpoint untuk daftar akun
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

    session = get_session()
    new_account = Account(
        nik=account.nik,
        nama=account.nama,
        no_hp=account.no_hp,
        no_rekening=str(random.randint(100000, 999999)),
    )
    session.add(new_account)
    close_session(session)

    return_msg = {
        "remark": "success",
        "data": {
            "no_rekening": new_account.no_rekening,
        }
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=return_msg)

# endpoint untuk tabung - menambah saldo
@app.post("/tabung")
def tabung(transaksi: TransaksiRequest):
    session = get_session()
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
    close_session(session)

    return_msg = {
        "remark": "success",
        "data": {
            "saldo": account.saldo
        }
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=return_msg)

# endpoint untuk tarik - mengurangi saldo
@app.post("/tarik")
def tarik(transaksi: TransaksiRequest):
    session = get_session()
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
    close_session(session)

    return_msg = {
        "remark": "success",
        "data": {
            "saldo": account.saldo
        }
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=return_msg)

# endpoint untuk cek saldo
@app.get("/saldo/{no_rekening}")
def get_saldo(no_rekening: str):
    session = get_session()
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

    close_session(session)
    return JSONResponse(status_code=status.HTTP_200_OK, content=return_msg)

# endpoint untuk mengecek mutasi
@app.get("/mutasi/{no_rekening}")
def get_mutasi(no_rekening: str):
    session = get_session()
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

    close_session(session)
    return JSONResponse(status_code=status.HTTP_200_OK, content=return_msg)

def delete_test_data():
    session = get_session()
    all_test_account = session.query(Account).filter(Account.nama.like('%test_case%')).all()
    for test_data in all_test_account:
        session.query(Transaksi).filter(Transaksi.no_rekening == test_data.no_rekening).delete()
        session.delete(test_data)
    close_session(session)