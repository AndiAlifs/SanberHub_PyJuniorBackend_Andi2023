from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

uri = URL.create(
    drivername="postgresql",
    username="root",
    password="root",
    host="localhost",
    port="5432",
    database="sanberhub_pyjun",
)

engine = create_engine(uri)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class Account(Base):
    __tablename__ = "account"
    nik = Column(String, primary_key=True)
    nama = Column(String)
    no_hp = Column(String)
    no_rekening = Column(String, nullable=True)
    saldo = Column(Integer, default=0)

class Transaksi(Base):
    __tablename__ = "transaksi"
    id = Column(Integer, primary_key=True)
    no_rekening = Column(String)
    nominal = Column(Integer)
    waktu = Column(DateTime)
    kode_transaksi = Column(String)

Base.metadata.create_all(engine)
session.close()