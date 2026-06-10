from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

class ChatRequest(BaseModel):
    client_id: int
    text: str

# Connexion à la base SQLite
def get_db_connection():
    conn = sqlite3.connect("banque.db")  # ⚠️ adapte le nom de ton fichier DB
    conn.row_factory = sqlite3.Row
    return conn

@router.post("/")
def chatbot_reply(request: ChatRequest):
    text = request.text.lower()
    client_id = request.client_id
    conn = get_db_connection()
    cursor = conn.cursor()

    # Vérifier le solde du client
    if "solde" in text:
        cursor.execute("SELECT solde FROM clients WHERE id = ?", (client_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"reply": f"Votre solde actuel est de {row['solde']} €."}
        return {"reply": "Client introuvable."}

    # Créer un crédit
    elif "crédit" in text:
        montant = 1000  # exemple fixe
        cursor.execute("INSERT INTO credits (client_id, montant) VALUES (?, ?)", (client_id, montant))
        conn.commit()
        conn.close()
        return {"reply": f"Votre demande de crédit de {montant} € a été enregistrée."}

    # Créer une transaction
    elif "transaction" in text:
        montant = 200  # exemple fixe
        type_tx = "paiement"
        cursor.execute("INSERT INTO transactions (client_id, montant, type) VALUES (?, ?, ?)", (client_id, montant, type_tx))
        conn.commit()
        conn.close()
        return {"reply": f"Votre transaction de {montant} € a été effectuée."}

    # Vérifier alertes de fraude
    elif "fraude" in text:
        cursor.execute("SELECT * FROM alertes WHERE client_id = ?", (client_id,))
        alertes = cursor.fetchall()
        conn.close()
        if alertes:
            return {"reply": f"⚠️ Attention, {len(alertes)} alertes de fraude détectées sur votre compte."}
        return {"reply": "✅ Aucune fraude détectée sur vos transactions."}

    # Réponse par défaut
    conn.close()
    return {"reply": "Je peux vous aider à consulter votre solde, créer un crédit ou une transaction, et vérifier la fraude."}
