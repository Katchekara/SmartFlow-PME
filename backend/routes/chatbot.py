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
    conn = sqlite3.connect("banque.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- Scoring prédictif ---
def entrainer_modele():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.solde,
               (SELECT SUM(montant) FROM transactions WHERE client_id = c.id AND type='revenu') as revenus,
               (SELECT SUM(montant) FROM transactions WHERE client_id = c.id AND type IN ('paiement','retrait')) as depenses,
               (SELECT COUNT(*) FROM credits WHERE client_id = c.id) as nb_credits,
               (SELECT COUNT(*) FROM alertes WHERE client_id = c.id) as nb_alertes,
               CASE WHEN c.solde < 0 OR (SELECT COUNT(*) FROM alertes WHERE client_id = c.id) > 0 THEN 1 ELSE 0 END as defaut
        FROM clients c
    """)
    data = cursor.fetchall()
    conn.close()

    X, y = [], []
    for row in data:
        solde = row["solde"]
        revenus = row["revenus"] or 0
        depenses = row["depenses"] or 0
        nb_credits = row["nb_credits"]
        nb_alertes = row["nb_alertes"]
        defaut = row["defaut"]
        X.append([solde, revenus, depenses, nb_credits, nb_alertes])
        y.append(defaut)

    # ✅ Vérification ici
    if not X or len(set(y)) < 2:
        return None

    model = LogisticRegression()
    model.fit(np.array(X), np.array(y))
    return model

def predire_defaut(client_id, model):
    if not model:
        return 1.0  # valeur par défaut
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT solde,
               (SELECT SUM(montant) FROM transactions WHERE client_id = ? AND type='revenu'),
               (SELECT SUM(montant) FROM transactions WHERE client_id = ? AND type IN ('paiement','retrait')),
               (SELECT COUNT(*) FROM credits WHERE client_id = ?),
               (SELECT COUNT(*) FROM alertes WHERE client_id = ?)
    """, (client_id, client_id, client_id, client_id))
    row = cursor.fetchone()
    conn.close()

    if not row :
        return 1.0

    solde, revenus, depenses, nb_credits, nb_alertes = row
    solde = solde or 0
    revenus = revenus or 0
    depenses = depenses or 0
    nb_credits = nb_credits or 0
    nb_alertes = nb_alertes or 0

    X_test = np.array([[solde, revenus, depenses, nb_credits, nb_alertes]])
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
        SELECT solde,
               (SELECT SUM(montant) FROM transactions WHERE client_id = ? AND type='revenu'),
               (SELECT SUM(montant) FROM transactions WHERE client_id = ? AND type IN ('paiement','retrait')),
               (SELECT COUNT(*) FROM alertes WHERE client_id = ?)
    """, (client_id, client_id, client_id))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Inconnu"

    solde, revenus, depenses, alertes = row
    solde = solde or 0
    revenus = revenus or 0
    depenses = depenses or 0
    alertes = alertes or 0


    if alertes > 0 or solde < 0:
        return "À risque"
    elif revenus > depenses * 1.5:
        return "Épargnant"
    elif depenses > revenus * 0.8:
        return "Dépensier"
    else:
        return "Standard"


# --- Fraude proactive ---
def verifier_fraude(client_id: int) -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT montant, type FROM transactions WHERE client_id = ?", (client_id,))
    transactions = cursor.fetchall()
    conn.close()

    alertes = []
    if not transactions:
        return alertes

    montants = [m for m, t in transactions]
    moyenne = sum(montants) / len(montants)

    for m, t in transactions:
        if m > moyenne * 3:
            alertes.append(f"Transaction suspecte : {m} € (supérieure à 3x la moyenne).")

    if len(transactions) > 5:
        alertes.append("Activité inhabituelle : plus de 5 transactions récentes.")

    return alertes

# --- Prévention proactive ---
def prevention_proactive(client_id: int) -> list:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT montant FROM transactions WHERE client_id = ?", (client_id,))
    transactions = cursor.fetchall()

    cursor.execute("SELECT solde FROM clients WHERE id = ?", (client_id,))
    solde_row = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM credits WHERE client_id = ?", (client_id,))
    nb_credits = cursor.fetchone()[0]
    conn.close()

    alertes = []

    if solde_row and solde_row[0] < 0 and nb_credits > 2:
        alertes.append("⚠️ Risque de surendettement détecté.")

    if transactions:
        montants = np.array([m[0] for m in transactions])
        moyenne = np.mean(montants)
        ecart_type = np.std(montants)
        for m in montants:
            if ecart_type > 0 and abs(m - moyenne) > 3 * ecart_type:
                alertes.append(f"⚠️ Transaction inhabituelle détectée : {m} €.")

    return alertes

# --- Reporting automatique ---
def generer_reporting(client_id: int) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT solde FROM clients WHERE id = ?", (client_id,))
    solde = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM transactions WHERE client_id = ?", (client_id,))
    nb_tx = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alertes WHERE client_id = ?", (client_id,))
    nb_alertes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM credits WHERE client_id = ?", (client_id,))
    nb_credits = cursor.fetchone()[0]

    conn.close()

    rapport = {
        "client_id": client_id,
        "solde": solde,
        "transactions": nb_tx,
        "credits": nb_credits,
        "alertes": nb_alertes
    }
    return rapport

# --- Chatbot principal ---
@router.post("/")
def chatbot_reply(request: ChatRequest):
    text = request.text.lower()
    client_id = request.client_id
    conn = get_db_connection()
    cursor = conn.cursor()

    # Solde
    if "solde" in text:
        cursor.execute("SELECT solde FROM clients WHERE id = ?", (client_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"reply": f"Votre solde actuel est de {row['solde']} €."}
        return {"reply": "Client introuvable."}

    # Crédit intelligent avec scoring
       
    elif "crédit" in text:
        model = entrainer_modele()
        if not model:  # modèle non entraînable
            conn.close()
            return {"reply": "⚠️ Pas assez de données pour calculer le risque de crédit."}

        proba_defaut = predire_defaut(client_id, model)
        if proba_defaut < 0.4:
            montant = 1000
            cursor.execute("INSERT INTO credits (client_id, montant) VALUES (?, ?)", (client_id, montant))
            conn.commit()
            conn.close()
            return {"reply": f"✅ Crédit accordé. Risque de défaut estimé à {proba_defaut:.2f}."}
        else:
            conn.close()
            return {"reply": f"❌ Crédit refusé. Risque trop élevé ({proba_defaut:.2f})."}

    # Transaction
    elif "transaction" in text:
        montant = 200
        type_tx = "paiement"
        cursor.execute("INSERT INTO transactions (client_id, montant, type) VALUES (?, ?, ?)", (client_id, montant, type_tx))
        conn.commit()
        conn.close()
        return {"reply": f"Votre transaction de {montant} € a été effectuée."}

    # Fraude proactive
    elif "fraude" in text or "conformité" in text:
        alertes_dynamiques = verifier_fraude(client_id)
        conn.close()
        if alertes_dynamiques:
            return {"reply": f"⚠️ Alertes détectées : {', '.join(alertes_dynamiques)}"}
        return {"reply": "✅ Aucune fraude détectée selon les règles dynamiques."}

    # Segmentation
    elif "profil" in text or "segmentation" in text:
        profil = segmenter_client(client_id)
        conn.close()
        return {"reply": f"Votre profil financier est : {profil}."}

    # Prévention proactive
    elif "prévention" in text or "alerte" in text:
        alertes = prevention_proactive(client_id)
        conn.close()
        if alertes:
            return {"reply": " | ".join(alertes)}
        else:
            return {"reply": "✅ Aucun risque détecté pour le moment."}

    # Reporting
    elif "reporting" in text or "rapport" in text:
        rapport = generer_reporting(client_id)
        conn.close()
        return {"reply": f"📊 Rapport client {client_id} : Solde={rapport['solde']} €, "
                         f"Transactions={rapport['transactions']}, "
                         f"Crédits={rapport['credits']}, "
                         f"Alertes={rapport['alertes']}"}

    # Par défaut
    conn.close()
    return {"reply": "Je peux vous aider à consulter votre solde, demander un crédit, effectuer une transaction, "
                     "vérifier la fraude, voir votre profil, activer la prévention proactive ou générer un reporting."}
