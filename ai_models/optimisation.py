# ============================================
# SmartFlow PME - Optimisation des Modèles IA
# Développeur : TAONDEYANDE Wendmanegda Jean-Claude
# ============================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import os

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

# ============================================
# BLOC 1 - RÉCUPÉRER LES DONNÉES
# ============================================

def generer_donnees():
    np.random.seed(42)
    N = 500

    data = {
        "chiffre_affaires":     np.random.randint(500_000,  50_000_000, N),
        "anciennete_ans":       np.random.randint(1,        20,         N),
        "nb_employes":          np.random.randint(1,        50,         N),
        "retards_paiement":     np.random.randint(0,        10,         N),
        "montant_dette":        np.random.randint(0,        20_000_000, N),
        "transactions_mobile":  np.random.randint(10,       500,        N),
        "secteur": np.random.choice(
            ["commerce", "agriculture", "services", "artisanat"], N),
    }

    df = pd.DataFrame(data)
    le = LabelEncoder()
    df["secteur"] = le.fit_transform(df["secteur"])

    def score(row):
        p = 0
        if row["chiffre_affaires"]    > 5_000_000: p += 2
        if row["anciennete_ans"]      > 3:          p += 2
        if row["retards_paiement"]    < 3:          p += 2
        if row["montant_dette"]       < 5_000_000:  p += 2
        if row["transactions_mobile"] > 100:        p += 1
        if row["nb_employes"]         > 5:          p += 1
        return 1 if p >= 6 else 0

    df["credit_accorde"] = df.apply(score, axis=1)

    X = df.drop("credit_accorde", axis=1)
    y = df["credit_accorde"]

    return train_test_split(X, y, test_size=0.2, random_state=42)

# ============================================
# BLOC 2 - COMPARER LES ALGORITHMES
# ============================================

def comparer_algorithmes(X_train, X_test, y_train, y_test):
    print("\n📊 COMPARAISON DES ALGORITHMES")
    print("-" * 50)

    algorithmes = {
        "Random Forest":         RandomForestClassifier(n_estimators=100, random_state=42),
        "Gradient Boosting":     GradientBoostingClassifier(n_estimators=100, random_state=42),
        "Régression Logistique": LogisticRegression(max_iter=1000, random_state=42),
        "K-Nearest Neighbors":   KNeighborsClassifier(n_neighbors=5),
    }

    resultats = {}

    for nom, algo in algorithmes.items():
        algo.fit(X_train, y_train)
        y_pred    = algo.predict(X_test)
        precision = accuracy_score(y_test, y_pred) * 100
        cv_scores = cross_val_score(algo, X_train, y_train, cv=5)
        cv_moyen  = cv_scores.mean() * 100

        resultats[nom] = {
            "precision": precision,
            "cv_moyen":  cv_moyen,
            "cv_std":    cv_scores.std() * 100,
        }

        print(f"\n🔹 {nom}")
        print(f"   Précision test     : {precision:.2f}%")
        print(f"   Validation croisée : {cv_moyen:.2f}% ± {cv_scores.std()*100:.2f}%")

    return resultats, algorithmes

# ============================================
# BLOC 3 - OPTIMISER RANDOM FOREST
# ============================================

def optimiser_random_forest(X_train, X_test, y_train, y_test):
    print("\n\n⚙️  OPTIMISATION RANDOM FOREST (GridSearchCV)")
    print("-" * 50)

    parametres = {
        "n_estimators":      [50, 100, 200],
        "max_depth":         [None, 5, 10],
        "min_samples_split": [2, 5],
    }

    rf   = RandomForestClassifier(random_state=42)
    grid = GridSearchCV(rf, parametres, cv=5,
                        scoring="accuracy", n_jobs=-1, verbose=0)

    print("⏳ Recherche des meilleurs paramètres...")
    grid.fit(X_train, y_train)

    print(f"✅ Meilleurs paramètres : {grid.best_params_}")
    print(f"✅ Meilleure précision  : {grid.best_score_*100:.2f}%")

    meilleur  = grid.best_estimator_
    y_pred    = meilleur.predict(X_test)
    precision = accuracy_score(y_test, y_pred) * 100
    print(f"✅ Précision sur test   : {precision:.2f}%")

    return meilleur, grid.best_params_, precision

# ============================================
# BLOC 4 - GRAPHIQUE CORRIGÉ
# ============================================

def afficher_comparaison(resultats, precision_optimisee):
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor("#F8F9FA")

    noms       = list(resultats.keys()) + ["RF Optimisé ⭐"]
    precisions = [r["precision"] for r in resultats.values()] + [precision_optimisee]
    cv_moyens  = [r["cv_moyen"]  for r in resultats.values()] + [precision_optimisee]

    # Couleurs apaisantes — doré pour le meilleur
    couleurs = ["#3498DB", "#2ECC71", "#F39C12", "#9B59B6", "#F1C40F"]

    for ax, valeurs, titre, xlabel in [
        (axes[0], precisions, "Précision sur données test (%)", "Précision (%)"),
        (axes[1], cv_moyens,  "Validation croisée — Score moyen (%)", "Score CV (%)"),
    ]:
        bars = ax.barh(noms, valeurs,
                       color=couleurs[:len(noms)],
                       alpha=0.85, height=0.5)
        ax.set_xlim(65, 105)
        ax.set_title(titre, fontweight="bold", pad=12)
        ax.set_xlabel(xlabel)
        ax.set_facecolor("#FFFFFF")

        # Labels DANS les barres — plus de chevauchement
        for bar, val in zip(bars, valeurs):
            x_pos = bar.get_x() + bar.get_width() - 1.5
            ax.text(x_pos,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}%",
                    va="center", ha="right",
                    fontsize=10, fontweight="bold",
                    color="white")

    plt.suptitle(
        "SmartFlow PME — Comparaison & Optimisation des Modèles IA",
        fontsize=13, fontweight="bold", y=1.02
    )
    plt.tight_layout()
    plt.savefig("ai_models/comparaison_modeles.png",
                dpi=150, bbox_inches="tight",
                facecolor="#F8F9FA")
    plt.show()
    print("✅ Graphique comparaison sauvegardé !")

# ============================================
# BLOC 5 - SAUVEGARDER LE MODÈLE OPTIMISÉ
# ============================================

def sauvegarder_optimise(modele_optimise):
    os.makedirs("ai_models/models", exist_ok=True)
    joblib.dump(modele_optimise,
                "ai_models/models/modele_credit_optimise.joblib")
    print("\n✅ Modèle optimisé sauvegardé !")
    print("   → ai_models/models/modele_credit_optimise.joblib")

# ============================================
# BLOC 6 - RAPPORT FINAL
# ============================================

def rapport_optimisation(resultats, best_params, precision_optimisee):
    print(f"\n{'='*55}")
    print(f"  SmartFlow PME — RAPPORT D'OPTIMISATION")
    print(f"{'='*55}")

    print(f"\n🏆 CLASSEMENT DES ALGORITHMES")
    classes = sorted(resultats.items(),
                     key=lambda x: x[1]["precision"], reverse=True)
    for i, (nom, res) in enumerate(classes):
        medal = ["🥇", "🥈", "🥉", "4️⃣"][i]
        print(f"   {medal} {nom:<25} : {res['precision']:.2f}%")

    print(f"\n⚙️  MODÈLE OPTIMISÉ (Random Forest)")
    print(f"   Paramètres : {best_params}")
    print(f"   Précision  : {precision_optimisee:.2f}%")

    meilleur_nom = classes[0][0]
    print(f"\n✅ RECOMMANDATION : Utiliser {meilleur_nom}")
    print(f"   C'est l'algorithme le plus performant")
    print(f"   pour le scoring crédit PME africaines.")
    print(f"\n{'='*55}\n")

# ============================================
# LANCEMENT
# ============================================

if __name__ == "__main__":
    print("⏳ Chargement des données...")
    X_train, X_test, y_train, y_test = generer_donnees()
    print(f"✅ Données prêtes : {len(X_train)} entraînement, "
          f"{len(X_test)} test")

    resultats, algos = comparer_algorithmes(
        X_train, X_test, y_train, y_test)

    modele_opt, best_params, prec_opt = optimiser_random_forest(
        X_train, X_test, y_train, y_test)

    rapport_optimisation(resultats, best_params, prec_opt)
    afficher_comparaison(resultats, prec_opt)
    sauvegarder_optimise(modele_opt)