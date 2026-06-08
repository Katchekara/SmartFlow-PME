import os
import joblib
import numpy as np
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.db import get_db
from backend.database.schema import Client, Alerte
from datetime import datetime

router = APIRouter(prefix="/fraud", tags=["Fraud Detection"])

# Construire chemin absolu vers le modèle de fraude
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "ai_models", "models", "modele_fraude.joblib")

fraud_model = joblib.load(MODEL_PATH)

# Schéma de requête pour vérifier une transaction
class TransactionCheck(BaseModel):
    client_id: int
    montant: float
    type: str  # ex: "virement", "paiement", "retrait"

# Endpoint POST : détection de fraude
@router.post("/")
def check_transaction(tx: TransactionCheck, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == tx.client_id).first()
    if not client:
        return {"error": "Client introuvable"}

    # Préparer les features pour le modèle
    features = np.array([[
        client.revenu,
        client.age,
        tx.montant,
        1 if tx.type == "virement" else 0,   # encodage simplifié du type
        client.historique_credit
    ]])

    prediction = fraud_model.predict(features)[0]

    if prediction == -1:  # IsolationForest retourne -1 pour anomalie
        decision = "Fraude suspectée"
        # Sauvegarde alerte en base
        alerte = Alerte(
            client_id=tx.client_id,
            type="fraude",
            message=f"Transaction suspecte détectée: {tx.type} de {tx.montant}",
            date=datetime.utcnow()
        )
        db.add(alerte)
        db.commit()
        db.refresh(alerte)
        return {"decision": decision, "alerte": alerte}
    else:
        return {"decision": "Transaction normale"}

# Endpoint GET : liste des alertes
@router.get("/alertes")
def list_alertes(db: Session = Depends(get_db)):
    return db.query(Alerte).all()
