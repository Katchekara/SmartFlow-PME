# backend/routes/chatbot.py
from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3
import numpy as np
from sklearn.linear_model import LogisticRegression

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

class ChatRequest(BaseModel):
    client_id: int
    text: str

# --- Connexion DB ---
def get_db_connection():
    conn = sqlite3.connect("smartflow.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- Scoring prédictif ---
def entrainer_modele():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.revenu,
               (SELECT COUNT(*) FROM credits WHERE client_id = c.id) as nb_credits,
               (SELECT COUNT(*) FROM alertes WHERE client_id = c.id) as nb_alertes,
               c.historique_credit,
               CASE WHEN c.historique_credit < 2 OR
                    (SELECT COUNT(*) FROM alertes WHERE client_id = c.id) > 0
                    THEN 1 ELSE 0 END as defaut
        FROM clients c
    """)
    data = cursor.fetchall()
    conn.close()

    X, y = [], []
    for row in data:
        X.append([
            row["revenu"] or 0,
            row["nb_credits"] or 0,
            row["nb_alertes"] or 0,
            row["historique_credit"] or 0,
        ])
        y.append(row["defaut"])

    if not X or len(set(y)) < 2:
        return None

    model = LogisticRegression()
    model.fit(np.array(X), np.array(y))
    return model

def predire_defaut(client_id, model):
    if not model:
        return 1.0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT revenu, historique_credit,
               (SELECT COUNT(*) FROM credits WHERE client_id = ?),
               (SELECT COUNT(*) FROM alertes WHERE client_id = ?)
        FROM clients WHERE id = ?
    """, (client_id, client_id, client_id))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return 1.0

    revenu        = row[0] or 0
    historique    = row[1] or 0
    nb_credits    = row[2] or 0
    nb_alertes    = row[3] or 0

    X_test = np.array([[revenu, nb_credits, nb_alertes, historique]])
    try:
        proba = model.predict_proba(X_test)[0][1]
    except Exception:
        return 1.0
    return proba

# --- Segmentation dynamique ---
def segmenter_client(client_id: int) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT revenu, historique_credit,
               (SELECT COUNT(*) FROM alertes WHERE client_id = ?) as nb_alertes,
               (SELECT COUNT(*) FROM transactions WHERE client_id = ?) as nb_tx
        FROM clients WHERE id = ?
    """, (client_id, client_id, client_id))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Inconnu"

    revenu     = row["revenu"] or 0
    historique = row["historique_credit"] or 0
    nb_alertes = row["nb_alertes"] or 0
    nb_tx      = row["nb_tx"] or 0

    if nb_alertes > 0 or historique < 2:
        return "À risque"
    elif revenu > 10_000_000 and historique >= 5:
        return "Épargnant"
    elif nb_tx > 10:
        return "Actif"
    else:
        return "Standard"

# --- Fraude proactive ---
def verifier_fraude(client_id: int) -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT montant, type FROM transactions WHERE client_id = ?",
        (client_id,)
    )
    transactions = cursor.fetchall()
    conn.close()

    alertes = []
    if not transactions:
        return alertes

    montants = [row[0] for row in transactions]
    moyenne  = sum(montants) / len(montants)

    for m, t in transactions:
        if m > moyenne * 3:
            alertes.append(
                f"Transaction suspecte : {m:,.0f} FCFA (supérieure à 3x la moyenne)."
            )
    if len(transactions) > 5:
        alertes.append("Activité inhabituelle : plus de 5 transactions récentes.")

    return alertes

# --- Prévention proactive ---
def prevention_proactive(client_id: int) -> list:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT montant FROM transactions WHERE client_id = ?", (client_id,)
    )
    transactions = cursor.fetchall()

    cursor.execute(
        "SELECT revenu, historique_credit FROM clients WHERE id = ?", (client_id,)
    )
    client_row = cursor.fetchone()

    cursor.execute(
        "SELECT COUNT(*) FROM credits WHERE client_id = ?", (client_id,)
    )
    nb_credits = cursor.fetchone()[0]
    conn.close()

    alertes = []

    if client_row:
        revenu     = client_row[0] or 0
        historique = client_row[1] or 0
        if historique < 2 and nb_credits > 2:
            alertes.append("⚠️ Risque de surendettement détecté.")
        if revenu < 500_000:
            alertes.append("⚠️ Revenu faible — surveiller les dépenses.")

    if transactions:
        montants   = np.array([m[0] for m in transactions])
        moyenne    = np.mean(montants)
        ecart_type = np.std(montants)
        for m in montants:
            if ecart_type > 0 and abs(m - moyenne) > 3 * ecart_type:
                alertes.append(
                    f"⚠️ Transaction inhabituelle détectée : {m:,.0f} FCFA."
                )

    return alertes

# --- Reporting automatique ---
def generer_reporting(client_id: int) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT nom, revenu, historique_credit FROM clients WHERE id = ?",
        (client_id,)
    )
    client = cursor.fetchone()

    cursor.execute(
        "SELECT COUNT(*) FROM transactions WHERE client_id = ?", (client_id,)
    )
    nb_tx = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM alertes WHERE client_id = ?", (client_id,)
    )
    nb_alertes = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*), SUM(montant_demande) FROM credits WHERE client_id = ?",
        (client_id,)
    )
    credit_row = cursor.fetchone()
    conn.close()

    return {
        "client_id":    client_id,
        "nom":          client["nom"] if client else "Inconnu",
        "revenu":       client["revenu"] if client else 0,
        "historique":   client["historique_credit"] if client else 0,
        "transactions": nb_tx,
        "credits":      credit_row[0] or 0,
        "montant_credits": credit_row[1] or 0,
        "alertes":      nb_alertes,
    }

# --- Chatbot principal ---
@router.post("/")
def chatbot_reply(request: ChatRequest):
    text      = request.text.lower()
    client_id = request.client_id

    conn   = get_db_connection()
    cursor = conn.cursor()

    # Vérifier que le client existe
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()
    if not client:
        conn.close()
        return {"reply": f"❌ Client #{client_id} introuvable. Créez d'abord un client via la page Crédit IA."}

    nom = client["nom"]

    # Solde / revenu
    if "solde" in text or "revenu" in text:
        conn.close()
        return {"reply": f"💰 Bonjour {nom} ! Votre revenu enregistré est de {client['revenu']:,.0f} FCFA. Historique crédit : {client['historique_credit']}/10."}

    # Crédit
    elif "crédit" in text or "credit" in text:
        model        = entrainer_modele()
        proba_defaut = predire_defaut(client_id, model)
        conn.close()
        if proba_defaut < 0.4:
            return {"reply": f"✅ {nom}, votre profil est favorable pour un crédit ! Risque de défaut estimé : {proba_defaut*100:.0f}%. Utilisez la page 💳 Crédit IA pour soumettre une demande complète."}
        else:
            return {"reply": f"❌ {nom}, votre profil présente un risque élevé ({proba_defaut*100:.0f}%). Conseil : améliorez votre historique de paiement avant de faire une demande."}

    # Transaction
    elif "transaction" in text:
        cursor.execute(
            "INSERT INTO transactions (client_id, montant, type) VALUES (?, ?, ?)",
            (client_id, 50000, "paiement")
        )
        conn.commit()
        conn.close()
        return {"reply": f"✅ Transaction de 50 000 FCFA enregistrée pour {nom}."}

    # Fraude
    elif "fraude" in text or "conformité" in text:
        alertes = verifier_fraude(client_id)
        conn.close()
        if alertes:
            return {"reply": f"⚠️ Alertes détectées pour {nom} :\n" + "\n".join(alertes)}
        return {"reply": f"✅ Aucune transaction suspecte détectée pour {nom}."}

    # Profil / segmentation
    elif "profil" in text or "segment" in text:
        profil = segmenter_client(client_id)
        conn.close()
        descriptions = {
            "Épargnant":  "Excellent profil financier — revenus stables et bon historique.",
            "Actif":      "Client très actif en transactions — surveiller les dépenses.",
            "Standard":   "Profil standard — continuer à maintenir un bon historique.",
            "À risque":   "Profil à risque — des alertes ont été détectées sur votre compte.",
            "Inconnu":    "Profil non déterminé — données insuffisantes.",
        }
        return {"reply": f"👤 {nom}, votre profil financier : **{profil}**\n{descriptions.get(profil, '')}"}

    # Prévention
    elif "prévention" in text or "alerte" in text or "risque" in text:
        alertes = prevention_proactive(client_id)
        conn.close()
        if alertes:
            return {"reply": f"⚠️ Alertes préventives pour {nom} :\n" + "\n".join(alertes)}
        return {"reply": f"✅ Aucun risque détecté pour {nom} pour le moment."}

    # Reporting
    elif "reporting" in text or "rapport" in text:
        rapport = generer_reporting(client_id)
        conn.close()
        return {"reply": (
            f"📊 Rapport de {rapport['nom']} (#{client_id}) :\n"
            f"• Revenu : {rapport['revenu']:,.0f} FCFA\n"
            f"• Historique crédit : {rapport['historique']}/10\n"
            f"• Transactions : {rapport['transactions']}\n"
            f"• Crédits demandés : {rapport['credits']} ({rapport['montant_credits']:,.0f} FCFA)\n"
            f"• Alertes fraude : {rapport['alertes']}"
        )}

    # Aide
    elif "aide" in text or "help" in text or "?" in text:
        conn.close()
        return {"reply": (
            f"🤖 Bonjour {nom} ! Je peux vous aider avec :\n"
            "• **solde** — voir votre revenu et historique\n"
            "• **crédit** — évaluer vos chances d'obtenir un crédit\n"
            "• **transaction** — enregistrer une transaction\n"
            "• **fraude** — vérifier les transactions suspectes\n"
            "• **profil** — voir votre segmentation client\n"
            "• **prévention** — alertes proactives sur votre compte\n"
            "• **reporting** — rapport financier complet"
        )}

    # Par défaut
    conn.close()
    return {"reply": (
        f"Bonjour {nom} ! Je n'ai pas compris votre demande. "
        "Tapez **aide** pour voir ce que je peux faire pour vous."
    )}