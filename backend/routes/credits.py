# backend/routes/credits.py

import joblib
import numpy as np
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.db import get_db
from backend.database.schema import Client, Credit
from datetime import datetime

router = APIRouter(prefix="/credits", tags=["Credits"])

credit_model = joblib.load("ai_models/models/modele_credit.joblib")
label_encoder = joblib.load("ai_models/models/label_encoder.joblib")

class CreditCreate(BaseModel):
    client_id: int
    montant_demande: float
    secteur: str

@router.post("/")
def create_credit(credit: CreditCreate, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == credit.client_id).first()
    if not client:
        return {"error": "Client introuvable"}

    secteur_encoded = label_encoder.transform([credit.secteur])[0]
    features = np.array([[
        client.revenu,
        client.age,
        10,
        0,
        2000000,
        150,
        secteur_encoded
    ]])

    prediction = credit_model.predict(features)[0]
    proba = credit_model.predict_proba(features)[0][1]
    decision = "Accepté" if prediction == 1 else "Refusé"

    db_credit = Credit(
        client_id=credit.client_id,
        montant_demande=credit.montant_demande,
        score_credit=proba,
        decision=decision,
        date_demande=datetime.utcnow()
    )
    db.add(db_credit)
    db.commit()
    db.refresh(db_credit)
    return db_credit

@router.get("/")
def list_credits(db: Session = Depends(get_db)):
    return db.query(Credit).all()
