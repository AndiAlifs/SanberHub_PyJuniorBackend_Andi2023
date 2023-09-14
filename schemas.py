from pydantic import BaseModel

class AccountRequest(BaseModel):
    nik: str
    nama: str
    no_hp: str

    class Config:
        from_attributes = True

class TransaksiRequest(BaseModel):
    no_rekening: str
    nominal: int

    class Config:
        from_attributes = True