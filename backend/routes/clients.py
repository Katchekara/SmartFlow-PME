from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.db import get_db
from backend.database.schema import Client

router = APIRouter(prefix="/clients", tags=["Clients"])

class ClientCreate(BaseModel):
    nom:               str
    age:               int
    revenu:            float
    historique_credit: int = 0

@router.post("/")
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.get("/")
def list_clients(db: Session = Depends(get_db)):
    return db.query(Client).all()

@router.get("/{client_id}")
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        return {"error": "Client introuvable"}
    return client