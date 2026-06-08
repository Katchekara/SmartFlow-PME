from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.database.schema import Client, Credit, Alerte   # <-- ajout des modèles manquants
import requests
from datetime import datetime

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

class ChatMessage(BaseModel):
    client_id: int | None = None
    text: str

# Hugging Face API config
HF_TOKEN = "***REMOVED***"  # <-- ton vrai token
API_URL = "https://api-inference.huggingface.co/models/bert-base-uncased"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}  # <-- correction : HEADERS → headers

def query_hf(user_input: str):
    response = requests.post(API_URL, headers=headers, json={"inputs": user_input})
    return response.json()

@router.post("/")
def chatbot_reply(msg: ChatMessage, db: Session = Depends(get_db)):
    text = msg.text.lower()
    reply = None

    # 🔹 Logique métier SmartFlow PME
    if "solde" in text and msg.client_id:
        client = db.query(Client).filter(Client.id == msg.client_id).first()
        if client:
            reply = f"Votre solde actuel est de {client.revenu} FCFA."

    elif "credit" in text and msg.client_id:
        credit = db.query(Credit).filter(Credit.client_id == msg.client_id).order_by(Credit.date_demande.desc()).first()
        if credit:
            reply = f"Votre dernière demande de crédit ({credit.montant_demande} FCFA) a été {credit.decision}."
        else:
            reply = "Vous pouvez faire une demande de crédit via l’endpoint /credits."

    elif "fraude" in text and msg.client_id:
        alerte = db.query(Alerte).filter(Alerte.client_id == msg.client_id).order_by(Alerte.date.desc()).first()
        if alerte:
            reply = f"⚠️ Alerte fraude détectée : {alerte.message}"
        else:
            reply = "Aucune fraude détectée sur vos transactions récentes."

    # 🔹 Si pas de logique métier → appel Hugging Face pour réponse naturelle
    if not reply:
        data = query_hf(msg.text)
        if isinstance(data, list) and "generated_text" in data[0]:
            reply = data[0]["generated_text"]
        else:
            reply = "Je n’ai pas pu générer de réponse."

    # 🔹 Sauvegarde historique (optionnel)
    db.execute(
        "INSERT INTO chat_history (client_id, message, reply, date) VALUES (?, ?, ?, ?)",
        (msg.client_id, msg.text, reply, datetime.utcnow())
    )
    db.commit()

    return {"reply": reply}
