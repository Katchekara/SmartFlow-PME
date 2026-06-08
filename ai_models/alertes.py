# ============================================
# SmartFlow PME - Système d'Alertes Automatiques
# Développeur : TAONDEYANDE Wendmanegda Jean-Claude
# ============================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ============================================
# BLOC 1 - SIMULER LES DONNÉES DE TRÉSORERIE
# D'UNE PME SUR 90 JOURS
# ============================================

def generer_tresorerie_pme(nom_pme="PME Alpha"):
    np.random.seed(42)
    aujourd_hui = datetime.today()
    dates = [aujourd_hui - timedelta(days=i) for i in range(90, 0, -1)]

    solde_initial = 5_000_000  # 5 millions FCFA
    soldes = [solde_initial]

    for i in range(1, 90):
        entree  = np.random.randint(0,       800_000)
        sortie  = np.random.randint(200_000, 900_000)
        nouveau = soldes[-1] + entree - sortie
        soldes.append(max(nouveau, 0))

    df = pd.DataFrame({
        "date":   dates,
        "solde":  soldes,
    })
    df["pme"] = nom_pme
    return df

# ============================================
# BLOC 2 - ANALYSER ET DÉTECTER LES ALERTES
# ============================================

SEUIL_DANGER   = 500_000    # En dessous = DANGER
SEUIL_ALERTE   = 1_500_000  # En dessous = ALERTE
SEUIL_ATTENTION = 3_000_000  # En dessous = ATTENTION

def analyser_tresorerie(df):
    alertes = []
    dernier_solde = df["solde"].iloc[-1]
    solde_moyen   = df["solde"].mean()
    tendance      = df["solde"].iloc[-7:].mean() - df["solde"].iloc[-14:-7].mean()

    # Niveau d'alerte selon solde actuel
    if dernier_solde < SEUIL_DANGER:
        niveau  = "🔴 DANGER"
        message = "Trésorerie critique ! Action immédiate requise."
    elif dernier_solde < SEUIL_ALERTE:
        niveau  = "🟠 ALERTE"
        message = "Trésorerie faible. Surveiller les dépenses."
    elif dernier_solde < SEUIL_ATTENTION:
        niveau  = "🟡 ATTENTION"
        message = "Trésorerie en baisse. Rester vigilant."
    else:
        niveau  = "🟢 NORMAL"
        message = "Trésorerie saine."

    alertes.append({
        "type":    "SOLDE ACTUEL",
        "niveau":  niveau,
        "valeur":  f"{dernier_solde:,.0f} FCFA",
        "message": message,
    })

    # Alerte tendance
    if tendance < -200_000:
        alertes.append({
            "type":    "TENDANCE",
            "niveau":  "🟠 ALERTE",
            "valeur":  f"{tendance:,.0f} FCFA/semaine",
            "message": "Baisse continue détectée sur 7 jours.",
        })
    elif tendance > 100_000:
        alertes.append({
            "type":    "TENDANCE",
            "niveau":  "🟢 POSITIF",
            "valeur":  f"{tendance:,.0f} FCFA/semaine",
            "message": "Trésorerie en amélioration.",
        })

    # Alerte jours critiques
    jours_danger = (df["solde"] < SEUIL_DANGER).sum()
    if jours_danger > 5:
        alertes.append({
            "type":    "JOURS CRITIQUES",
            "niveau":  "🔴 DANGER",
            "valeur":  f"{jours_danger} jours",
            "message": f"Trésorerie sous {SEUIL_DANGER:,} FCFA pendant {jours_danger} jours.",
        })

    return alertes, dernier_solde, solde_moyen, tendance

# ============================================
# BLOC 3 - PRÉDIRE LES 30 PROCHAINS JOURS
# ============================================

def predire_tresorerie(df, jours=30):
    dernier_solde = df["solde"].iloc[-1]
    variations    = df["solde"].diff().dropna()
    variation_moy = variations.mean()
    variation_std = variations.std()

    predictions = [dernier_solde]
    aujourd_hui  = datetime.today()

    for i in range(1, jours + 1):
        variation  = np.random.normal(variation_moy, variation_std)
        nouveau    = predictions[-1] + variation
        predictions.append(max(nouveau, 0))

    dates_futures = [aujourd_hui + timedelta(days=i) for i in range(jours + 1)]

    df_pred = pd.DataFrame({
        "date":  dates_futures,
        "solde": predictions,
    })

    # Alertes sur prédictions
    jours_danger_futurs = (df_pred["solde"] < SEUIL_DANGER).sum()
    if jours_danger_futurs > 0:
        print(f"\n⚠️  PRÉDICTION : {jours_danger_futurs} jours critiques dans les 30 prochains jours !")

    return df_pred

# ============================================
# BLOC 4 - AFFICHER LE GRAPHIQUE
# ============================================

def afficher_graphique(df_historique, df_prediction, nom_pme):
    fig, ax = plt.subplots(figsize=(14, 6))

    # Historique
    ax.plot(df_historique["date"], df_historique["solde"],
            color="#3498DB", linewidth=2, label="Historique 90 jours")

    # Prédiction
    ax.plot(df_prediction["date"], df_prediction["solde"],
            color="#F39C12", linewidth=2, linestyle="--", label="Prédiction 30 jours")

    # Zones de seuil
    ax.axhline(SEUIL_DANGER,    color="#E74C3C", linestyle=":", alpha=0.7, label="Seuil Danger")
    ax.axhline(SEUIL_ALERTE,    color="#E67E22", linestyle=":", alpha=0.7, label="Seuil Alerte")
    ax.axhline(SEUIL_ATTENTION, color="#F1C40F", linestyle=":", alpha=0.7, label="Seuil Attention")

    # Zone prédiction en gris clair
    ax.axvspan(df_prediction["date"].iloc[0],
               df_prediction["date"].iloc[-1],
               alpha=0.1, color="orange", label="Zone prédiction")

    ax.set_title(f"SmartFlow PME — Trésorerie & Prédictions : {nom_pme}", fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Solde (FCFA)")
    ax.legend(loc="upper left")
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x/1_000_000:.1f}M")
    )
    plt.tight_layout()
    plt.savefig("ai_models/graphique_tresorerie.png")
    plt.show()
    print("✅ Graphique sauvegardé !")

# ============================================
# BLOC 5 - RAPPORT COMPLET
# ============================================

def generer_rapport(nom_pme="PME Alpha"):
    print(f"\n{'='*55}")
    print(f"  SmartFlow PME — Rapport d'Alertes : {nom_pme}")
    print(f"  Date : {datetime.today().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*55}")

    df           = generer_tresorerie_pme(nom_pme)
    alertes, dernier_solde, solde_moyen, tendance = analyser_tresorerie(df)
    df_pred      = predire_tresorerie(df)

    print(f"\n📊 RÉSUMÉ FINANCIER")
    print(f"   Solde actuel  : {dernier_solde:>15,.0f} FCFA")
    print(f"   Solde moyen   : {solde_moyen:>15,.0f} FCFA")
    print(f"   Tendance/sem  : {tendance:>15,.0f} FCFA")

    print(f"\n🔔 ALERTES DÉTECTÉES ({len(alertes)})")
    for a in alertes:
        print(f"\n   [{a['niveau']}] {a['type']}")
        print(f"   Valeur  : {a['valeur']}")
        print(f"   Message : {a['message']}")

    print(f"\n📈 PRÉDICTION 30 JOURS")
    print(f"   Solde prédit fin de période : "
          f"{df_pred['solde'].iloc[-1]:,.0f} FCFA")

    afficher_graphique(df, df_pred, nom_pme)
    print(f"\n{'='*55}\n")

# ============================================
# LANCEMENT
# ============================================

if __name__ == "__main__":
    generer_rapport("PME Kaboré & Frères")