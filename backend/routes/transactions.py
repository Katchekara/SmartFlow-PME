from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.db import get_db
from backend.database.schema import Transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])

class TransactionCreate(BaseModel):
    client_id:       int
    montant:         float
    type:            str
    nb_transactions: int = 1

@router.post("/")
def create_transaction(tx: TransactionCreate, db: Session = Depends(get_db)):
    db_tx = Transaction(**tx.model_dump())
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

@router.get("/")
def list_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()

@router.get("/{client_id}")
def transactions_client(client_id: int, db: Session = Depends(get_db)):
    return db.query(Transaction).filter(
        Transaction.client_id == client_id
    ).all()