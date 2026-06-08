from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base   # ← CORRECT


class Client(Base):
    __tablename__ = "clients"
    id                = Column(Integer, primary_key=True, index=True)
    nom               = Column(String, index=True)
    age               = Column(Integer)
    revenu            = Column(Float)
    historique_credit = Column(Integer, default=0)
    date_creation     = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="client")
    credits      = relationship("Credit",      back_populates="client")
    alertes      = relationship("Alerte",      back_populates="client")

class Transaction(Base):
    __tablename__ = "transactions"
    id              = Column(Integer, primary_key=True, index=True)
    client_id       = Column(Integer, ForeignKey("clients.id"))
    montant         = Column(Float)
    type            = Column(String)
    nb_transactions = Column(Integer, default=1)
    date            = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="transactions")

class Credit(Base):
    __tablename__ = "credits"
    id              = Column(Integer, primary_key=True, index=True)
    client_id       = Column(Integer, ForeignKey("clients.id"))
    montant_demande = Column(Float)
    score_credit    = Column(Float)
    decision        = Column(String)
    date_demande    = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="credits")

class Alerte(Base):
    __tablename__ = "alertes"
    id        = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    type      = Column(String)
    message   = Column(String)
    date      = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="alertes")