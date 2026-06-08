# ============================================
# SmartFlow PME - Génération Automatique de Rapports
# Développeur : TAONDEYANDE Wendmanegda Jean-Claude
# ============================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from datetime import datetime, timedelta

# ============================================
# BLOC 1 - SIMULER LES DONNÉES D'UNE PME
# ============================================

def generer_donnees_pme(nom_pme="PME Kaboré & Frères"):
    np.random.seed(42)
    aujourd_hui = datetime.today()
    mois = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
            "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]

    # Données mensuelles
    revenus   = np.random.randint(2_000_000, 15_000_000, 12)
    charges   = np.random.randint(1_000_000,  8_000_000, 12)
    benefices = revenus - charges

    df_mensuel = pd.DataFrame({
        "mois":     mois,
        "revenus":  revenus,
        "charges":  charges,
        "benefice": benefices,
    })

    # Données trésorerie 30 jours
    dates  = [aujourd_hui - timedelta(days=i) for i in range(30, 0, -1)]
    soldes = [5_000_000]
    for _ in range(29):
        variation = np.random.randint(-800_000, 600_000)
        soldes.append(max(soldes[-1] + variation, 0))

    df_tresorerie = pd.DataFrame({
        "date":  dates,
        "solde": soldes,
    })

    # Données clients
    nb_clients = 15
    df_clients = pd.DataFrame({
        "client":       [f"Client {i+1}" for i in range(nb_clients)],
        "chiffre_affaires": np.random.randint(100_000, 3_000_000, nb_clients),
        "statut": np.random.choice(["Payé", "En attente", "En retard"], nb_clients),
    })

    return df_mensuel, df_tresorerie, df_clients

# ============================================
# BLOC 2 - CALCULER LES KPIs
# ============================================

def calculer_kpis(df_mensuel, df_tresorerie, df_clients):
    kpis = {}

    # Financiers
    kpis["revenu_total"]      = df_mensuel["revenus"].sum()
    kpis["charges_totales"]   = df_mensuel["charges"].sum()
    kpis["benefice_total"]    = df_mensuel["benefice"].sum()
    kpis["marge_beneficiaire"]= round(
        kpis["benefice_total"] / kpis["revenu_total"] * 100, 1)
    kpis["meilleur_mois"]     = df_mensuel.loc[
        df_mensuel["benefice"].idxmax(), "mois"]
    kpis["pire_mois"]         = df_mensuel.loc[
        df_mensuel["benefice"].idxmin(), "mois"]

    # Trésorerie
    kpis["solde_actuel"]      = df_tresorerie["solde"].iloc[-1]
    kpis["solde_moyen"]       = df_tresorerie["solde"].mean()
    kpis["solde_min"]         = df_tresorerie["solde"].min()

    # Clients
    kpis["nb_clients"]        = len(df_clients)
    kpis["clients_payes"]     = (df_clients["statut"] == "Payé").sum()
    kpis["clients_retard"]    = (df_clients["statut"] == "En retard").sum()
    kpis["ca_moyen_client"]   = df_clients["chiffre_affaires"].mean()
    kpis["taux_recouvrement"] = round(
        kpis["clients_payes"] / kpis["nb_clients"] * 100, 1)

    return kpis

# ============================================
# BLOC 3 - GÉNÉRER LE RAPPORT VISUEL
# ============================================

def generer_rapport_visuel(nom_pme, df_mensuel, df_tresorerie, df_clients, kpis):

    fig = plt.figure(figsize=(18, 14))
    fig.patch.set_facecolor("#F8F9FA")
    gs  = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

    # ── Titre principal ──────────────────────────────
    fig.suptitle(
        f"SmartFlow PME — Rapport Financier Annuel\n{nom_pme}  |  "
        f"Généré le {datetime.today().strftime('%d/%m/%Y à %H:%M')}",
        fontsize=15, fontweight="bold", color="#1A1A2E", y=0.98
    )

    # ── Graphique 1 : Revenus vs Charges ─────────────
    ax1 = fig.add_subplot(gs[0, :2])
    x   = np.arange(len(df_mensuel["mois"]))
    w   = 0.35
    ax1.bar(x - w/2, df_mensuel["revenus"]  / 1_000_000,
            w, label="Revenus",  color="#2ECC71", alpha=0.85)
    ax1.bar(x + w/2, df_mensuel["charges"]  / 1_000_000,
            w, label="Charges",  color="#E74C3C", alpha=0.85)
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_mensuel["mois"])
    ax1.set_title("Revenus vs Charges (M FCFA)", fontweight="bold")
    ax1.set_ylabel("Millions FCFA")
    ax1.legend()
    ax1.set_facecolor("#FFFFFF")

    # ── Graphique 2 : Bénéfice mensuel ───────────────
    ax2   = fig.add_subplot(gs[0, 2])
    coul  = ["#2ECC71" if b >= 0 else "#E74C3C"
             for b in df_mensuel["benefice"]]
    ax2.bar(df_mensuel["mois"], df_mensuel["benefice"] / 1_000_000,
            color=coul, alpha=0.85)
    ax2.axhline(0, color="black", linewidth=0.8)
    ax2.set_title("Bénéfice mensuel (M FCFA)", fontweight="bold")
    ax2.set_xticklabels(df_mensuel["mois"], rotation=45, fontsize=7)
    ax2.set_facecolor("#FFFFFF")

    # ── Graphique 3 : Trésorerie 30 jours ────────────
    ax3 = fig.add_subplot(gs[1, :2])
    ax3.plot(df_tresorerie["date"], df_tresorerie["solde"] / 1_000_000,
             color="#3498DB", linewidth=2)
    ax3.fill_between(df_tresorerie["date"],
                     df_tresorerie["solde"] / 1_000_000,
                     alpha=0.15, color="#3498DB")
    ax3.axhline(0.5, color="#E74C3C", linestyle="--",
                alpha=0.7, label="Seuil danger")
    ax3.set_title("Trésorerie — 30 derniers jours (M FCFA)",
                  fontweight="bold")
    ax3.set_ylabel("Millions FCFA")
    ax3.legend()
    ax3.set_facecolor("#FFFFFF")

    # ── Graphique 4 : Statut clients ─────────────────
    ax4    = fig.add_subplot(gs[1, 2])
    statuts = df_clients["statut"].value_counts()
    coul4   = ["#2ECC71", "#F39C12", "#E74C3C"]
    ax4.pie(statuts.values, labels=statuts.index,
            colors=coul4[:len(statuts)],
            autopct="%1.1f%%", startangle=90)
    ax4.set_title("Statut des clients", fontweight="bold")

    # ── KPIs cards ───────────────────────────────────
    ax5 = fig.add_subplot(gs[2, :])
    ax5.axis("off")

    kpi_items = [
        ("💰 Revenu Total",      f"{kpis['revenu_total']/1_000_000:.1f}M FCFA"),
        ("📈 Bénéfice Total",    f"{kpis['benefice_total']/1_000_000:.1f}M FCFA"),
        ("📊 Marge",             f"{kpis['marge_beneficiaire']}%"),
        ("🏦 Solde Actuel",      f"{kpis['solde_actuel']/1_000_000:.1f}M FCFA"),
        ("👥 Clients",           f"{kpis['nb_clients']}"),
        ("✅ Taux Recouvrement", f"{kpis['taux_recouvrement']}%"),
        ("🌟 Meilleur Mois",     kpis['meilleur_mois']),
        ("⚠️  Pire Mois",        kpis['pire_mois']),
    ]

    for i, (label, valeur) in enumerate(kpi_items):
        x_pos = (i % 4) * 0.26 + 0.02
        y_pos = 0.55 if i < 4 else 0.05

        ax5.add_patch(plt.Rectangle(
            (x_pos, y_pos), 0.23, 0.38,
            fill=True, facecolor="#EBF5FB",
            edgecolor="#3498DB", linewidth=1.5,
            transform=ax5.transAxes
        ))
        ax5.text(x_pos + 0.115, y_pos + 0.26, label,
                 ha="center", va="center", fontsize=9,
                 color="#5A5A6A", transform=ax5.transAxes)
        ax5.text(x_pos + 0.115, y_pos + 0.12, valeur,
                 ha="center", va="center", fontsize=13,
                 fontweight="bold", color="#1A1A2E",
                 transform=ax5.transAxes)

    ax5.set_title("📋 Indicateurs Clés de Performance (KPIs)",
                  fontweight="bold", pad=10)

    plt.savefig("ai_models/rapport_financier.png",
                dpi=150, bbox_inches="tight",
                facecolor="#F8F9FA")
    plt.show()
    print("✅ Rapport visuel sauvegardé !")

# ============================================
# BLOC 4 - RAPPORT TEXTE DANS LE TERMINAL
# ============================================

def afficher_rapport_terminal(nom_pme, kpis):
    print(f"\n{'='*55}")
    print(f"  SmartFlow PME — RAPPORT FINANCIER ANNUEL")
    print(f"  PME    : {nom_pme}")
    print(f"  Date   : {datetime.today().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*55}")

    print(f"\n💰 PERFORMANCE FINANCIÈRE")
    print(f"   Revenu total       : {kpis['revenu_total']:>15,.0f} FCFA")
    print(f"   Charges totales    : {kpis['charges_totales']:>15,.0f} FCFA")
    print(f"   Bénéfice total     : {kpis['benefice_total']:>15,.0f} FCFA")
    print(f"   Marge bénéficiaire : {kpis['marge_beneficiaire']:>14.1f} %")
    print(f"   Meilleur mois      : {kpis['meilleur_mois']}")
    print(f"   Pire mois          : {kpis['pire_mois']}")

    print(f"\n🏦 TRÉSORERIE")
    print(f"   Solde actuel       : {kpis['solde_actuel']:>15,.0f} FCFA")
    print(f"   Solde moyen        : {kpis['solde_moyen']:>15,.0f} FCFA")
    print(f"   Solde minimum      : {kpis['solde_min']:>15,.0f} FCFA")

    print(f"\n👥 CLIENTS")
    print(f"   Nombre de clients  : {kpis['nb_clients']}")
    print(f"   Clients payés      : {kpis['clients_payes']}")
    print(f"   Clients en retard  : {kpis['clients_retard']}")
    print(f"   Taux recouvrement  : {kpis['taux_recouvrement']} %")
    print(f"   CA moyen/client    : {kpis['ca_moyen_client']:>15,.0f} FCFA")

    # Recommandations IA
    print(f"\n🤖 RECOMMANDATIONS IA SMARTFLOW")
    if kpis["marge_beneficiaire"] < 20:
        print("   ⚠️  Marge faible — réduire les charges opérationnelles")
    else:
        print("   ✅ Marge saine — maintenir le cap")

    if kpis["solde_actuel"] < 1_000_000:
        print("   🔴 Trésorerie critique — action urgente requise")
    elif kpis["solde_actuel"] < 3_000_000:
        print("   🟡 Trésorerie à surveiller")
    else:
        print("   🟢 Trésorerie saine")

    if kpis["taux_recouvrement"] < 60:
        print("   ⚠️  Taux recouvrement faible — activer les relances")
    else:
        print("   ✅ Recouvrement satisfaisant")

    print(f"\n{'='*55}\n")

# ============================================
# LANCEMENT
# ============================================

if __name__ == "__main__":
    NOM_PME = "PME Kaboré & Frères"

    df_mensuel, df_tresorerie, df_clients = generer_donnees_pme(NOM_PME)
    kpis = calculer_kpis(df_mensuel, df_tresorerie, df_clients)

    afficher_rapport_terminal(NOM_PME, kpis)
    generer_rapport_visuel(NOM_PME, df_mensuel,
                           df_tresorerie, df_clients, kpis)