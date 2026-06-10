# ============================================
# SmartFlow PME - Routes IA Complètes
# ============================================

from fastapi import APIRouter
from pydantic import BaseModel
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

router = APIRouter(prefix="/ia", tags=["IA Modules"])

# ============================================
# ENDPOINT 1 — ALERTES TRÉSORERIE
# ============================================

@router.get("/alertes-tresorerie/{nom_pme}")
def alertes_tresorerie(nom_pme: str):
    from ai_models.alertes import generer_tresorerie_pme, analyser_tresorerie, predire_tresorerie

    df        = generer_tresorerie_pme(nom_pme)
    alertes, dernier_solde, solde_moyen, tendance = analyser_tresorerie(df)
    df_pred   = predire_tresorerie(df)

    return {
        "pme":           nom_pme,
        "solde_actuel":  round(dernier_solde),
        "solde_moyen":   round(solde_moyen),
        "tendance":      round(tendance),
        "solde_predit":  round(df_pred["solde"].iloc[-1]),
        "alertes":       alertes,
        "historique": [
            {"date": str(row["date"].date()), "solde": round(row["solde"])}
            for _, row in df.iterrows()
        ],
        "prediction": [
            {"date": str(row["date"].date()), "solde": round(row["solde"])}
            for _, row in df_pred.iterrows()
        ],
    }

# ============================================
# ENDPOINT 2 — RELANCES CLIENTS
# ============================================

@router.get("/relances/{nom_pme}")
def relances_clients(nom_pme: str):
    from ai_models.relances import (generer_clients_retard,
                                     classifier_relance,
                                     calculer_risque,
                                     generer_message)

    df = generer_clients_retard()
    df["niveau_relance"] = df.apply(lambda r: classifier_relance(r)[0], axis=1)
    df["priorite"]       = df.apply(lambda r: classifier_relance(r)[1], axis=1)
    df["risque"]         = df.apply(calculer_risque, axis=1)
    df["message"]        = df.apply(lambda r: generer_message(r, nom_pme), axis=1)
    df = df.sort_values("priorite", ascending=False)

    return {
        "pme":              nom_pme,
        "total_clients":    len(df),
        "total_montant_du": int(df["montant_du"].sum()),
        "clients": [
            {
                "nom":           row["nom_client"],
                "montant_du":    int(row["montant_du"]),
                "jours_retard":  int(row["jours_retard"]),
                "niveau":        row["niveau_relance"],
                "risque":        row["risque"],
                "telephone":     row["telephone"],
                "message":       row["message"],
            }
            for _, row in df.iterrows()
        ]
    }

# ============================================
# ENDPOINT 3 — RAPPORT FINANCIER
# ============================================

@router.get("/rapport/{nom_pme}")
def rapport_financier(nom_pme: str):
    from ai_models.rapports import (generer_donnees_pme, calculer_kpis)

    df_mensuel, df_tresorerie, df_clients = generer_donnees_pme(nom_pme)
    kpis = calculer_kpis(df_mensuel, df_tresorerie, df_clients)

    return {
        "pme":  nom_pme,
        "kpis": {k: round(v, 2) if isinstance(v, float) else v
                 for k, v in kpis.items()},
        "mensuel": [
            {
                "mois":     row["mois"],
                "revenus":  int(row["revenus"]),
                "charges":  int(row["charges"]),
                "benefice": int(row["benefice"]),
            }
            for _, row in df_mensuel.iterrows()
        ],
        "tresorerie_30j": [
            {"date": str(row["date"].date()), "solde": round(row["solde"])}
            for _, row in df_tresorerie.iterrows()
        ],
        "statut_clients": df_clients["statut"].value_counts().to_dict(),
    }