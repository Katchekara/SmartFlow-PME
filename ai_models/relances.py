# ============================================
# SmartFlow PME - Système de Relances Automatiques
# Développeur : TAONDEYANDE Wendmanegda Jean-Claude
# ============================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ============================================
# BLOC 1 - SIMULER LES CLIENTS EN RETARD
# ============================================

def generer_clients_retard(nb_clients=20):
    np.random.seed(42)
    aujourd_hui = datetime.today()

    noms = [
        "Sawadogo Inoussa", "Compaoré Fatima", "Traoré Moussa",
        "Ouédraogo Aïcha", "Zongo Bernard", "Kaboré Sylvie",
        "Tapsoba Adama", "Nikiema Rasmata", "Belem Seydou",
        "Some Mariam", "Diallo Boubacar", "Coulibaly Awa",
        "Barry Hamidou", "Kinda Jeanne", "Nacoulma Pierre",
        "Rabo Salimata", "Toe Justin", "Dabo Aminata",
        "Guiro Lassana", "Konfe Rokia"
    ]

    data = {
        "nom_client":      noms[:nb_clients],
        "montant_du":      np.random.randint(50_000, 2_000_000, nb_clients),
        "jours_retard":    np.random.randint(1, 120, nb_clients),
        "nb_relances":     np.random.randint(0, 5,   nb_clients),
        "telephone":       [f"+226 7{np.random.randint(0,9)} {np.random.randint(10,99)} {np.random.randint(10,99)} {np.random.randint(10,99)}"
                           for _ in range(nb_clients)],
        "email":           [f"client{i+1}@email.bf" for i in range(nb_clients)],
        "derniere_relance": [
            (aujourd_hui - timedelta(days=np.random.randint(1, 30))).strftime("%d/%m/%Y")
            for _ in range(nb_clients)
        ],
    }

    df = pd.DataFrame(data)
    return df

# ============================================
# BLOC 2 - CLASSIFIER LE NIVEAU DE RELANCE
# ============================================

def classifier_relance(row):
    if row["jours_retard"] <= 15:
        return "RAPPEL DOUX", 1
    elif row["jours_retard"] <= 30:
        return "RELANCE STANDARD", 2
    elif row["jours_retard"] <= 60:
        return "RELANCE FERME", 3
    else:
        return "MISE EN DEMEURE", 4

# ============================================
# BLOC 3 - GÉNÉRER LE MESSAGE DE RELANCE
# ============================================

def generer_message(row, nom_pme="PME Kaboré & Frères"):
    niveau, _ = classifier_relance(row)
    montant   = f"{row['montant_du']:,.0f} FCFA"
    client    = row["nom_client"]
    today     = datetime.today().strftime("%d/%m/%Y")

    if niveau == "RAPPEL DOUX":
        return f"""Bonjour {client},

Nous espérons que vous allez bien.
Nous vous rappelons amicalement qu'une facture 
de {montant} est arrivée à échéance depuis 
{row['jours_retard']} jour(s).

Si vous avez déjà effectué le règlement, 
veuillez ignorer ce message.

Cordialement,
{nom_pme}
Date : {today}"""

    elif niveau == "RELANCE STANDARD":
        return f"""Bonjour {client},

Sauf erreur de notre part, nous n'avons pas 
reçu le règlement de votre facture de {montant}, 
échue depuis {row['jours_retard']} jours.

Nous vous remercions de procéder au règlement 
dans les meilleurs délais.

Cordialement,
{nom_pme}
Date : {today}"""

    elif niveau == "RELANCE FERME":
        return f"""Monsieur/Madame {client},

Malgré nos précédents rappels ({row['nb_relances']} relance(s)),
votre facture de {montant} reste impayée 
depuis {row['jours_retard']} jours.

Nous vous mettons en demeure de régler cette 
somme sous 8 jours ouvrables.

Sans réponse de votre part, nous nous verrons 
contraints de prendre les mesures nécessaires.

{nom_pme}
Date : {today}"""

    else:  # MISE EN DEMEURE
        return f"""MISE EN DEMEURE

Monsieur/Madame {client},

En l'absence de règlement de votre dette de 
{montant} depuis {row['jours_retard']} jours,
et après {row['nb_relances']} relance(s) restées 
sans suite, nous procédons à une mise en demeure 
officielle.

Vous disposez de 72 heures pour régulariser 
votre situation, faute de quoi ce dossier sera 
transmis à notre service contentieux.

{nom_pme}
Date : {today}"""

# ============================================
# BLOC 4 - SCORE DE RISQUE CLIENT
# ============================================

def calculer_risque(row):
    score = 0
    if row["jours_retard"]  > 60:  score += 3
    elif row["jours_retard"] > 30:  score += 2
    else:                           score += 1
    if row["nb_relances"]   > 3:   score += 2
    if row["montant_du"]    > 1_000_000: score += 1

    if score >= 5: return "🔴 ÉLEVÉ"
    elif score >= 3: return "🟠 MOYEN"
    else: return "🟢 FAIBLE"

# ============================================
# BLOC 5 - GRAPHIQUE RÉCAPITULATIF
# ============================================

def afficher_graphique(df):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Graphique 1 : Montants par niveau de relance
    niveaux = df["niveau_relance"].value_counts()
    couleurs = ["#2ECC71", "#F39C12", "#E67E22", "#E74C3C"]
    axes[0].bar(niveaux.index, niveaux.values, color=couleurs[:len(niveaux)])
    axes[0].set_title("Clients par niveau de relance")
    axes[0].set_xlabel("Niveau")
    axes[0].set_ylabel("Nombre de clients")
    axes[0].tick_params(axis="x", rotation=15)

    # Graphique 2 : Montants dus par niveau
    montants = df.groupby("niveau_relance")["montant_du"].sum()
    axes[1].bar(montants.index, montants.values / 1_000_000,
                color=couleurs[:len(montants)])
    axes[1].set_title("Montants dus par niveau (millions FCFA)")
    axes[1].set_xlabel("Niveau")
    axes[1].set_ylabel("Montant (M FCFA)")
    axes[1].tick_params(axis="x", rotation=15)

    plt.suptitle("SmartFlow PME — Tableau de bord Relances",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("ai_models/graphique_relances.png")
    plt.show()
    print("✅ Graphique sauvegardé !")

# ============================================
# BLOC 6 - RAPPORT COMPLET
# ============================================

def generer_rapport_relances(nom_pme="PME Kaboré & Frères"):
    print(f"\n{'='*55}")
    print(f"  SmartFlow PME — Rapport de Relances")
    print(f"  PME : {nom_pme}")
    print(f"  Date : {datetime.today().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*55}")

    df = generer_clients_retard()

    # Ajouter colonnes calculées
    df["niveau_relance"] = df.apply(
        lambda r: classifier_relance(r)[0], axis=1)
    df["priorite"]       = df.apply(
        lambda r: classifier_relance(r)[1], axis=1)
    df["risque"]         = df.apply(calculer_risque, axis=1)
    df["message"]        = df.apply(
        lambda r: generer_message(r, nom_pme), axis=1)

    # Trier par priorité
    df = df.sort_values("priorite", ascending=False)

    # Résumé
    total_du = df["montant_du"].sum()
    print(f"\n💰 RÉSUMÉ")
    print(f"   Clients en retard    : {len(df)}")
    print(f"   Total montant dû     : {total_du:,.0f} FCFA")
    print(f"   Montant moyen/client : {df['montant_du'].mean():,.0f} FCFA")

    print(f"\n📋 RÉPARTITION PAR NIVEAU")
    for niveau, count in df["niveau_relance"].value_counts().items():
        montant = df[df["niveau_relance"] == niveau]["montant_du"].sum()
        print(f"   {niveau:<20} : {count} clients — {montant:,.0f} FCFA")

    # Afficher les 3 cas les plus urgents avec leur message
    print(f"\n🚨 TOP 3 CAS URGENTS — Messages générés")
    print("-" * 55)
    for _, row in df.head(3).iterrows():
        print(f"\n👤 {row['nom_client']} | {row['risque']}")
        print(f"   Montant : {row['montant_du']:,.0f} FCFA")
        print(f"   Retard  : {row['jours_retard']} jours")
        print(f"   Tél     : {row['telephone']}")
        print(f"\n📱 MESSAGE :\n{row['message']}")
        print("-" * 55)

    afficher_graphique(df)
    return df

# ============================================
# LANCEMENT
# ============================================

if __name__ == "__main__":
    df_relances = generer_rapport_relances("PME Kaboré & Frères")