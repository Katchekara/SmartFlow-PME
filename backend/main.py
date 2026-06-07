from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sklearn.ensemble import IsolationForest
import numpy as np
from datetime import datetime

# --- Config DB SQLite ---
DATABASE_URL = "sqlite:///./smartflow.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Modèles SQLAlchemy ---
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    age = Column(Integer)
    revenu = Column(Float)
    historique_credit = Column(Integer, default=0)
    date_creation = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="client")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    montant = Column(Float)
    type = Column(String)  # paiement, retrait, virement
    nb_transactions = Column(Integer, default=1)
    date = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="transactions")

Base.metadata.create_all(bind=engine)

# --- FastAPI ---
app = FastAPI()

# --- Dépendance DB ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Schémas Pydantic ---
class ClientCreate(BaseModel):
    nom: str
    age: int
    revenu: float

class TransactionCreate(BaseModel):
    client_id: int
    montant: float
    type: str
    nb_transactions: int

class TransactionData(BaseModel):
    montant: float
    nb_transactions: int

# --- Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Hello Hackathon!"}

@app.post("/clients")
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = Client(nom=client.nom, age=client.age, revenu=client.revenu)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@app.get("/clients")
def list_clients(db: Session = Depends(get_db)):
    return db.query(Client).all()

@app.post("/transactions")
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = Transaction(
        client_id=transaction.client_id,
        montant=transaction.montant,
        type=transaction.type,
        nb_transactions=transaction.nb_transactions
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/transactions")
def list_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()

# --- Modèle IA pour fraude ---
fraud_model = IsolationForest(random_state=42)
fraud_model.fit([[100, 1], [200, 2], [300, 3], [400, 4]])  # données fictives

@app.post("/fraud_detection")
def fraud_detection(data: TransactionData):
    features = np.array([[data.montant, data.nb_transactions]])
    prediction = fraud_model.predict(features)[0]
    result = "Fraude détectée" if prediction == -1 else "Transaction normale"
    return {
        "montant": data.montant,
        "nb_transactions": data.nb_transactions,
        "resultat": result
    }

# --- Schéma Pydantic ---
class CreditCreate(BaseModel):
    client_id: int
    montant_demande: float

# --- Modèle SQLAlchemy ---
class Credit(Base):
    __tablename__ = "credits"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    montant_demande = Column(Float)
    score_credit = Column(Float)
    decision = Column(String)
    date_demande = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client")

# --- Endpoint POST /credits ---
@app.post("/credits")
def create_credit(credit: CreditCreate, db: Session = Depends(get_db)):
    # Récupérer le client
    client = db.query(Client).filter(Client.id == credit.client_id).first()
    if not client:
        return {"error": "Client introuvable"}

    # Exemple de calcul de score simple
    score = (client.revenu / (credit.montant_demande + 1)) + client.historique_credit * 0.1
    score = min(score / 100, 1.0)  # normalisation entre 0 et 1

    decision = "Accepté" if score >= 0.6 else "Refusé"

    db_credit = Credit(
        client_id=credit.client_id,
        montant_demande=credit.montant_demande,
        score_credit=score,
        decision=decision
    )
    db.add(db_credit)
    db.commit()
    db.refresh(db_credit)
    return db_credit

# --- Endpoint GET /credits ---
@app.get("/credits")
def list_credits(db: Session = Depends(get_db)):
    return db.query(Credit).all()
