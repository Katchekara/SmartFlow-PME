# backend/routes/fraud.py

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

# ── Chemins absolus vers les modèles ─────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "ai_models", "models", "modele_fraude.joblib")
ENCODER_PATH = os.path.join(BASE_DIR, "ai_models", "models", "label_encoder_fraude.joblib")

fraud_model    = joblib.load(MODEL_PATH)
fraud_encoder  = joblib.load(ENCODER_PATH)

# ── Schéma de requête ─────────────────────────────────
class TransactionCheck(BaseModel):
    client_id:            int
    montant:              float
    heure_transaction:    int    # 0-23
    nb_transactions_jour: int
    distance_km:          int
    nouveau_destinataire: int    # 0 ou 1
    echecs_recents:       int
    type_transaction:     str   # "depot","retrait","transfert","paiement"

# ── POST : détection de fraude ────────────────────────
@router.post("/")
def check_transaction(tx: TransactionCheck, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == tx.client_id).first()
    if not client:
        return {"error": "Client introuvable"}

    # Encoder le type de transaction
    try:
        type_encode = fraud_encoder.transform([tx.type_transaction])[0]
    except Exception:
        return {"error": f"Type transaction invalide : '{tx.type_transaction}'. "
                         f"Valeurs acceptées : depot, retrait, transfert, paiement"}

    # 7 features — exactement ce qu'attend notre modèle
    features = np.array([[
        tx.montant,
        tx.heure_transaction,
        tx.nb_transactions_jour,
        tx.distance_km,
        tx.nouveau_destinataire,
        tx.echecs_recents,
        type_encode
    ]])

    # Prédiction — RandomForest retourne 0 ou 1
    prediction  = fraud_model.predict(features)[0]
    probabilite = fraud_model.predict_proba(features)[0]
    risque      = round(probabilite[1] * 100, 1)

    if prediction == 1:
        decision = "Fraude suspectée"

        # Sauvegarder l'alerte en base
        alerte = Alerte(
            client_id = tx.client_id,
            type      = "fraude",
            message   = (
                f"Transaction suspecte : {tx.type_transaction} "
                f"de {tx.montant:,.0f} FCFA — "
                f"risque {risque}%"
            ),
            date = datetime.utcnow()
        )
        db.add(alerte)
        db.commit()
        db.refresh(alerte)

        return {
            "decision":      decision,
            "risque":        f"{risque}%",
            "action":        "Bloquer et alerter le propriétaire",
            "alerte":        alerte
        }

    else:
        return {
            "decision": "Transaction normale",
            "risque":   f"{risque}%",
            "action":   "Laisser passer"
        }

# ── GET : liste des alertes ───────────────────────────
@router.get("/alertes")
def list_alertes(db: Session = Depends(get_db)):
    return db.query(Alerte).all()

# ── GET : alertes d'un client spécifique ─────────────
@router.get("/alertes/{client_id}")
def alertes_client(client_id: int, db: Session = Depends(get_db)):
    alertes = db.query(Alerte).filter(
        Alerte.client_id == client_id
    ).all()
    if not alertes:
        return {"message": f"Aucune alerte pour le client {client_id}"}
    return alertes