from fastapi import APIRouter
import sqlite3
import numpy as np
from sklearn.linear_model import LogisticRegression

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_db_connection():
    conn = sqlite3.connect("banque.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- Scoring global ---
@router.get("/")
def dashboard_global():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom, solde FROM clients")
    clients = cursor.fetchall()
    conn.close()

    resultats = []
    for client in clients:
        resultats.append({
            "client_id": client["id"],
            "nom": client["nom"],
            "solde": client["solde"]
        })
    return {"clients": resultats}

# --- Scoring individuel ---
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

    if not X:
        return None

    model = LogisticRegression()
    model.fit(np.array(X), np.array(y))
    return model

def predire_defaut(client_id, model):
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

    if not row or not model:
        return 1.0

    solde, revenus, depenses, nb_credits, nb_alertes = row
    X_test = np.array([[solde, revenus or 0, depenses or 0, nb_credits, nb_alertes]])
    proba = model.predict_proba(X_test)[0][1]
    return proba

@router.get("/risk/{client_id}")
def dashboard_risk(client_id: int):
    model = entrainer_modele()
    proba_defaut = predire_defaut(client_id, model)
    return {"client_id": client_id, "risque_defaut": round(proba_defaut, 2)}

# --- Segmentation ---
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
    revenus = revenus or 0
    depenses = depenses or 0

    if alertes > 0 or solde < 0:
        return "À risque"
    elif revenus > depenses * 1.5:
        return "Épargnant"
    elif depenses > revenus * 0.8:
        return "Dépensier"
    else:
        return "Standard"

@router.get("/segments")
def dashboard_segments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom FROM clients")
    clients = cursor.fetchall()
    conn.close()

    resultats = []
    for client in clients:
        profil = segmenter_client(client["id"])
        resultats.append({
            "client_id": client["id"],
            "nom": client["nom"],
            "profil": profil
        })
    return {"segmentation_clients": resultats}

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

    # Surendettement
    if solde_row and solde_row[0] < 0 and nb_credits > 2:
        alertes.append("⚠️ Risque de surendettement détecté.")

    # Transactions inhabituelles (z-score)
    if transactions:
        montants = np.array([m[0] for m in transactions])
        moyenne = np.mean(montants)
        ecart_type = np.std(montants)
        for m in montants:
            if ecart_type > 0 and abs(m - moyenne) > 3 * ecart_type:
                alertes.append(f"⚠️ Transaction inhabituelle détectée : {m} €.")

    return alertes

@router.get("/prevention")
def dashboard_prevention():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom FROM clients")
    clients = cursor.fetchall()
    conn.close()

    resultats = []
    for client in clients:
        alertes = prevention_proactive(client["id"])
        resultats.append({
            "client_id": client["id"],
            "nom": client["nom"],
            "alertes": alertes if alertes else ["✅ Aucun risque détecté"]
        })
    return {"prevention_clients": resultats}
