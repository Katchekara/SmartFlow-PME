import os
import joblib
import numpy as np
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.db import get_db
from backend.database.schema import Client, Credit
from datetime import datetime

router = APIRouter(prefix="/credits", tags=["Credits"])

# Construire chemin absolu vers les modèles IA
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "ai_models", "models", "modele_credit.joblib")
ENCODER_PATH = os.path.join(BASE_DIR, "ai_models", "models", "label_encoder.joblib")

# Charger le modèle et l’encodeur
credit_model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

# Schéma de requête pour créer un crédit
class CreditCreate(BaseModel):
    client_id: int
    montant_demande: float
    secteur: str  # commerce, agriculture, services, artisanat

# Endpoint POST : créer un crédit
@router.post("/")
def create_credit(credit: CreditCreate, db: Session = Depends(get_db)):
    # Vérifier si le client existe
    client = db.query(Client).filter(Client.id == credit.client_id).first()
    if not client:
        return {"error": "Client introuvable"}

    # Encoder le secteur
    secteur_encoded = label_encoder.transform([credit.secteur])[0]

    # Préparer les features pour le modèle
    features = np.array([[
        client.revenu,          # chiffre d'affaires
        client.age,             # ancienneté simplifiée
        10,                     # nb_employes fictif
        0,                      # retards_paiement fictif
        2000000,                # montant_dette fictif
        150,                    # transactions_mobile fictif
        secteur_encoded
    ]])

    # Prédiction
    prediction = credit_model.predict(features)[0]
    proba = credit_model.predict_proba(features)[0][1]
    decision = "Accepté" if prediction == 1 else "Refusé"

    # Sauvegarde en base
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

# Endpoint GET : liste des crédits
@router.get("/")
def list_credits(db: Session = Depends(get_db)):
    return db.query(Credit).all()
