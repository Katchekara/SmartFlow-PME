# ============================================
# SmartFlow PME - Modèle de Scoring de Crédit
# Développeur : TAONDEYANDE Wendmanegda Jean-Claude
# ============================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder

# ============================================
# BLOC 2 - GÉNÉRATION DES DONNÉES PME
# ============================================

np.random.seed(42)  # Pour avoir toujours les mêmes résultats
N = 500  # Nombre de PME simulées

data = {
    "chiffre_affaires":     np.random.randint(500000,  50000000, N),
    "anciennete_ans":       np.random.randint(1,        20,       N),
    "nb_employes":          np.random.randint(1,        50,       N),
    "retards_paiement":     np.random.randint(0,        10,       N),
    "montant_dette":        np.random.randint(0,        20000000, N),
    "transactions_mobile":  np.random.randint(10,       500,      N),
    "secteur": np.random.choice(
        ["commerce", "agriculture", "services", "artisanat"], N
    ),
}

df = pd.DataFrame(data)

# ============================================
# BLOC 3 - CRÉER LE SCORE (ce que l'IA doit apprendre)
# 1 = crédit accordé   0 = crédit refusé
# ============================================

def calculer_score(row):
    points = 0
    if row["chiffre_affaires"] > 5000000:   points += 2
    if row["anciennete_ans"]   > 3:          points += 2
    if row["retards_paiement"] < 3:          points += 2
    if row["montant_dette"]    < 5000000:    points += 2
    if row["transactions_mobile"] > 100:     points += 1
    if row["nb_employes"]      > 5:          points += 1
    return 1 if points >= 6 else 0

df["credit_accorde"] = df.apply(calculer_score, axis=1)

print("✅ Données générées :", df.shape)
print(df["credit_accorde"].value_counts())

# ============================================
# BLOC 4 - PRÉPARER LES DONNÉES POUR L'IA
# ============================================

# Convertir le secteur (texte → chiffre)
le = LabelEncoder()
df["secteur"] = le.fit_transform(df["secteur"])

# Séparer les features (X) et la cible (y)
X = df.drop("credit_accorde", axis=1)
y = df["credit_accorde"]

# Diviser en données d'entraînement (80%) et de test (20%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\n✅ Entraînement : {X_train.shape[0]} PME")
print(f"✅ Test         : {X_test.shape[0]} PME")

# ============================================
# BLOC 5 - ENTRAÎNER LE MODÈLE IA
# ============================================

modele = RandomForestClassifier(
    n_estimators=100,   # 100 arbres de décision
    random_state=42
)

print("\n⏳ Entraînement en cours...")
modele.fit(X_train, y_train)
print("✅ Modèle entraîné !")

# ============================================
# BLOC 6 - ÉVALUER LA PRÉCISION DU MODÈLE
# ============================================

y_pred = modele.predict(X_test)

precision = accuracy_score(y_test, y_pred) * 100
print(f"\n🎯 Précision du modèle : {precision:.2f}%")
print("\n📊 Rapport détaillé :")
print(classification_report(y_test, y_pred,
      target_names=["Refusé", "Accordé"]))

# ============================================
# BLOC 7 - GRAPHIQUE : Importance des facteurs
# ============================================

importances = modele.feature_importances_
features    = X.columns

plt.figure(figsize=(10, 6))
plt.barh(features, importances, color="#E8500A")
plt.xlabel("Importance")
plt.title("SmartFlow PME — Facteurs décisifs pour le crédit")
plt.tight_layout()
plt.savefig("ai_models/importance_credit.png")
plt.show()
print("✅ Graphique sauvegardé !")

# ============================================
# BLOC 8 - SAUVEGARDER LE MODÈLE
# ============================================

os.makedirs("ai_models/models", exist_ok=True)
joblib.dump(modele, "ai_models/models/modele_credit.joblib")
joblib.dump(le,     "ai_models/models/label_encoder.joblib")

print("\n✅ Modèle sauvegardé dans ai_models/models/")

# ============================================
# BLOC 9 - TEST AVEC UNE VRAIE PME
# ============================================

print("\n--- TEST : Évaluation d'une PME ---")

pme_test = pd.DataFrame([{
    "chiffre_affaires":    8000000,
    "anciennete_ans":      5,
    "nb_employes":         12,
    "retards_paiement":    1,
    "montant_dette":       2000000,
    "transactions_mobile": 250,
    "secteur":             le.transform(["commerce"])[0],
}])

resultat = modele.predict(pme_test)[0]
probabilite = modele.predict_proba(pme_test)[0]

print(f"Décision : {'✅ Crédit ACCORDÉ' if resultat == 1 else '❌ Crédit REFUSÉ'}")
print(f"Probabilité d'accord : {probabilite[1]*100:.1f}%")