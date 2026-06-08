# ============================================
# SmartFlow PME - Modèle de Détection de Fraude
# Développeur : TAONDEYANDE Wendmanegda Jean-Claude
# ============================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

# ============================================
# BLOC 2 - GÉNÉRATION DES TRANSACTIONS
# ============================================

np.random.seed(42)
N = 1000  # 1000 transactions simulées

data = {
    "montant":              np.random.randint(500, 5000000, N),
    "heure_transaction":    np.random.randint(0, 23, N),
    "nb_transactions_jour": np.random.randint(1, 50, N),
    "distance_km":          np.random.randint(0, 500, N),
    "nouveau_destinataire":  np.random.randint(0, 1, N),
    "echecs_recents":       np.random.randint(0, 5, N),
    "type_transaction": np.random.choice(
        ["depot", "retrait", "transfert", "paiement"], N
    ),
}

df = pd.DataFrame(data)

# ============================================
# BLOC 3 - CRÉER LE LABEL FRAUDE
# 1 = transaction frauduleuse   0 = normale
# ============================================

def detecter_fraude(row):
    score = 0
    if row["montant"]              > 3000000: score += 2
    if row["heure_transaction"]    < 5:       score += 2  # heure suspecte
    if row["nb_transactions_jour"] > 20:      score += 2
    if row["distance_km"]          > 300:     score += 1
    if row["nouveau_destinataire"] == 1:      score += 1
    if row["echecs_recents"]       > 2:       score += 2
    return 1 if score >= 5 else 0

df["fraude"] = df.apply(detecter_fraude, axis=1)

print("✅ Transactions générées :", df.shape)
print(df["fraude"].value_counts())
print(f"   Fraudes : {df['fraude'].sum()} / {N} transactions")

# ============================================
# BLOC 4 - PRÉPARER LES DONNÉES
# ============================================

le = LabelEncoder()
df["type_transaction"] = le.fit_transform(df["type_transaction"])

X = df.drop("fraude", axis=1)
y = df["fraude"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\n✅ Entraînement : {X_train.shape[0]} transactions")
print(f"✅ Test         : {X_test.shape[0]} transactions")

# ============================================
# BLOC 5 - ENTRAÎNER LE MODÈLE
# ============================================

modele = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"  # important car les fraudes sont rares
)

print("\n⏳ Entraînement en cours...")
modele.fit(X_train, y_train)
print("✅ Modèle entraîné !")

# ============================================
# BLOC 6 - ÉVALUER LE MODÈLE
# ============================================

y_pred = modele.predict(X_test)

precision = accuracy_score(y_test, y_pred) * 100
print(f"\n🎯 Précision du modèle : {precision:.2f}%")
print("\n📊 Rapport détaillé :")
print(classification_report(y_test, y_pred,
      target_names=["Normale", "Fraude"]))

# ============================================
# BLOC 7 - GRAPHIQUE : Facteurs de fraude
# ============================================

importances = modele.feature_importances_
features    = X.columns

plt.figure(figsize=(10, 6))
plt.barh(features, importances, color="#C0392B")
plt.xlabel("Importance")
plt.title("SmartFlow PME — Facteurs de détection de fraude")
plt.tight_layout()
plt.savefig("ai_models/importance_fraude.png")
plt.show()
print("✅ Graphique sauvegardé !")

# ============================================
# BLOC 8 - SAUVEGARDER LE MODÈLE
# ============================================

os.makedirs("ai_models/models", exist_ok=True)
joblib.dump(modele, "ai_models/models/modele_fraude.joblib")
joblib.dump(le,     "ai_models/models/label_encoder_fraude.joblib")

print("\n✅ Modèle sauvegardé dans ai_models/models/")

# ============================================
# BLOC 9 - TEST AVEC UNE VRAIE TRANSACTION
# ============================================

print("\n--- TEST : Analyse d'une transaction suspecte ---")

transaction_test = pd.DataFrame([{
    "montant":              4500000,   # montant élevé
    "heure_transaction":    3,         # 3h du matin
    "nb_transactions_jour": 25,        # beaucoup de transactions
    "distance_km":          450,       # loin
    "nouveau_destinataire": 1,         # nouveau destinataire
    "echecs_recents":       3,         # échecs récents
    "type_transaction":     le.transform(["transfert"])[0],
}])

resultat    = modele.predict(transaction_test)[0]
probabilite = modele.predict_proba(transaction_test)[0]

print(f"Décision     : {'🚨 FRAUDE DÉTECTÉE' if resultat == 1 else '✅ Transaction NORMALE'}")
print(f"Probabilité  : {probabilite[1]*100:.1f}% de risque de fraude")

print("\n--- TEST : Transaction normale ---")

transaction_normale = pd.DataFrame([{
    "montant":              150000,
    "heure_transaction":    14,        # 14h
    "nb_transactions_jour": 3,
    "distance_km":          5,
    "nouveau_destinataire": 0,
    "echecs_recents":       0,
    "type_transaction":     le.transform(["paiement"])[0],
}])

resultat2    = modele.predict(transaction_normale)[0]
probabilite2 = modele.predict_proba(transaction_normale)[0]

print(f"Décision     : {'🚨 FRAUDE DÉTECTÉE' if resultat2 == 1 else '✅ Transaction NORMALE'}")
print(f"Probabilité  : {probabilite2[1]*100:.1f}% de risque de fraude")