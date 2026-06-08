# ============================================
# SmartFlow PME - Tests Unitaires Modèles IA
# Développeur : TAONDEYANDE Wendmanegda Jean-Claude
# ============================================

import pytest
import numpy as np
import pandas as pd
import joblib
import os
import sys

# Ajouter le dossier racine au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================
# CONFIGURATION — Chemins des modèles
# ============================================

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR   = os.path.join(BASE_DIR, "ai_models", "models")

MODEL_CREDIT  = os.path.join(MODELS_DIR, "modele_credit.joblib")
ENCODER_CREDIT= os.path.join(MODELS_DIR, "label_encoder.joblib")
MODEL_FRAUDE  = os.path.join(MODELS_DIR, "modele_fraude.joblib")
ENCODER_FRAUDE= os.path.join(MODELS_DIR, "label_encoder_fraude.joblib")

# ============================================
# FIXTURES — Données de test réutilisables
# ============================================

@pytest.fixture
def modele_credit():
    return joblib.load(MODEL_CREDIT)

@pytest.fixture
def encoder_credit():
    return joblib.load(ENCODER_CREDIT)

@pytest.fixture
def modele_fraude():
    return joblib.load(MODEL_FRAUDE)

@pytest.fixture
def encoder_fraude():
    return joblib.load(ENCODER_FRAUDE)

@pytest.fixture
def pme_favorable():
    """PME avec bon profil — crédit doit être accordé"""
    return {
        "chiffre_affaires":    10_000_000,
        "anciennete_ans":      8,
        "nb_employes":         15,
        "retards_paiement":    0,
        "montant_dette":       1_000_000,
        "transactions_mobile": 300,
        "secteur":             "commerce",
    }

@pytest.fixture
def pme_risquee():
    """PME avec mauvais profil — crédit doit être refusé"""
    return {
        "chiffre_affaires":    200_000,
        "anciennete_ans":      1,
        "nb_employes":         1,
        "retards_paiement":    8,
        "montant_dette":       15_000_000,
        "transactions_mobile": 5,
        "secteur":             "artisanat",
    }

@pytest.fixture
def transaction_suspecte():
    """Transaction frauduleuse évidente"""
    return {
        "montant":              4_500_000,
        "heure_transaction":    3,
        "nb_transactions_jour": 25,
        "distance_km":          450,
        "nouveau_destinataire": 1,
        "echecs_recents":       3,
        "type_transaction":     "transfert",
    }

@pytest.fixture
def transaction_normale():
    """Transaction normale"""
    return {
        "montant":              150_000,
        "heure_transaction":    14,
        "nb_transactions_jour": 2,
        "distance_km":          5,
        "nouveau_destinataire": 0,
        "echecs_recents":       0,
        "type_transaction":     "paiement",
    }

# ============================================
# TESTS — Chargement des modèles
# ============================================

class TestChargementModeles:

    def test_modele_credit_existe(self):
        """Le fichier modele_credit.joblib doit exister"""
        assert os.path.exists(MODEL_CREDIT), \
            "❌ modele_credit.joblib introuvable !"

    def test_encoder_credit_existe(self):
        """Le fichier label_encoder.joblib doit exister"""
        assert os.path.exists(ENCODER_CREDIT), \
            "❌ label_encoder.joblib introuvable !"

    def test_modele_fraude_existe(self):
        """Le fichier modele_fraude.joblib doit exister"""
        assert os.path.exists(MODEL_FRAUDE), \
            "❌ modele_fraude.joblib introuvable !"

    def test_encoder_fraude_existe(self):
        """Le fichier label_encoder_fraude.joblib doit exister"""
        assert os.path.exists(ENCODER_FRAUDE), \
            "❌ label_encoder_fraude.joblib introuvable !"

    def test_modele_credit_chargeable(self, modele_credit):
        """Le modèle crédit doit se charger sans erreur"""
        assert modele_credit is not None

    def test_modele_fraude_chargeable(self, modele_fraude):
        """Le modèle fraude doit se charger sans erreur"""
        assert modele_fraude is not None

# ============================================
# TESTS — Modèle de scoring crédit
# ============================================

class TestScoringCredit:

    def _preparer_features(self, pme, encoder):
        secteur_encode = encoder.transform([pme["secteur"]])[0]
        return np.array([[
            pme["chiffre_affaires"],
            pme["anciennete_ans"],
            pme["nb_employes"],
            pme["retards_paiement"],
            pme["montant_dette"],
            pme["transactions_mobile"],
            secteur_encode,
        ]])

    def test_prediction_retourne_0_ou_1(
            self, modele_credit, encoder_credit, pme_favorable):
        """La prédiction doit retourner 0 ou 1"""
        X = self._preparer_features(pme_favorable, encoder_credit)
        pred = modele_credit.predict(X)[0]
        assert pred in [0, 1], f"❌ Valeur inattendue : {pred}"

    def test_pme_favorable_acceptee(
            self, modele_credit, encoder_credit, pme_favorable):
        """Une PME avec bon profil doit être acceptée"""
        X = self._preparer_features(pme_favorable, encoder_credit)
        pred = modele_credit.predict(X)[0]
        assert pred == 1, "❌ PME favorable refusée — vérifier le modèle"

    def test_pme_risquee_refusee(
            self, modele_credit, encoder_credit, pme_risquee):
        """Une PME risquée doit être refusée"""
        X = self._preparer_features(pme_risquee, encoder_credit)
        pred = modele_credit.predict(X)[0]
        assert pred == 0, "❌ PME risquée acceptée — vérifier le modèle"

    def test_probabilite_entre_0_et_1(
            self, modele_credit, encoder_credit, pme_favorable):
        """La probabilité doit être entre 0 et 1"""
        X    = self._preparer_features(pme_favorable, encoder_credit)
        prob = modele_credit.predict_proba(X)[0]
        assert 0 <= prob[0] <= 1
        assert 0 <= prob[1] <= 1

    def test_secteurs_valides(self, modele_credit, encoder_credit):
        """Tous les secteurs valides doivent fonctionner"""
        secteurs = ["commerce", "agriculture", "services", "artisanat"]
        for secteur in secteurs:
            pme = {
                "chiffre_affaires": 5_000_000,
                "anciennete_ans": 5,
                "nb_employes": 10,
                "retards_paiement": 1,
                "montant_dette": 2_000_000,
                "transactions_mobile": 200,
                "secteur": secteur,
            }
            X    = self._preparer_features(pme, encoder_credit)
            pred = modele_credit.predict(X)[0]
            assert pred in [0, 1], f"❌ Erreur pour secteur : {secteur}"

    def test_precision_globale(self, modele_credit, encoder_credit):
        """La précision globale doit dépasser 90%"""
        from sklearn.preprocessing import LabelEncoder
        from sklearn.metrics import accuracy_score

        np.random.seed(42)
        N = 200
        le = encoder_credit

        data = {
            "chiffre_affaires":    np.random.randint(500_000, 50_000_000, N),
            "anciennete_ans":      np.random.randint(1, 20, N),
            "nb_employes":         np.random.randint(1, 50, N),
            "retards_paiement":    np.random.randint(0, 10, N),
            "montant_dette":       np.random.randint(0, 20_000_000, N),
            "transactions_mobile": np.random.randint(10, 500, N),
            "secteur": np.random.choice(
                ["commerce", "agriculture", "services", "artisanat"], N),
        }
        df = pd.DataFrame(data)
        df["secteur"] = le.transform(df["secteur"])

        def score(row):
            p = 0
            if row["chiffre_affaires"]    > 5_000_000: p += 2
            if row["anciennete_ans"]      > 3:          p += 2
            if row["retards_paiement"]    < 3:          p += 2
            if row["montant_dette"]       < 5_000_000:  p += 2
            if row["transactions_mobile"] > 100:        p += 1
            if row["nb_employes"]         > 5:          p += 1
            return 1 if p >= 6 else 0

        y_true = df.apply(score, axis=1)
        X      = df.drop(columns=[])
        y_pred = modele_credit.predict(X)
        acc    = accuracy_score(y_true, y_pred)
        assert acc >= 0.90, f"❌ Précision insuffisante : {acc*100:.1f}%"

# ============================================
# TESTS — Modèle de détection de fraude
# ============================================

class TestDetectionFraude:

    def _preparer_features(self, tx, encoder):
        type_encode = encoder.transform([tx["type_transaction"]])[0]
        return np.array([[
            tx["montant"],
            tx["heure_transaction"],
            tx["nb_transactions_jour"],
            tx["distance_km"],
            tx["nouveau_destinataire"],
            tx["echecs_recents"],
            type_encode,
        ]])

    def test_prediction_retourne_0_ou_1(
            self, modele_fraude, encoder_fraude, transaction_normale):
        """La prédiction doit retourner 0 ou 1"""
        X    = self._preparer_features(transaction_normale, encoder_fraude)
        pred = modele_fraude.predict(X)[0]
        assert pred in [0, 1], f"❌ Valeur inattendue : {pred}"

    def test_transaction_suspecte_detectee(
            self, modele_fraude, encoder_fraude, transaction_suspecte):
        """Une transaction suspecte doit être détectée"""
        X    = self._preparer_features(transaction_suspecte, encoder_fraude)
        pred = modele_fraude.predict(X)[0]
        assert pred == 1, "❌ Fraude non détectée !"

    def test_transaction_normale_acceptee(
            self, modele_fraude, encoder_fraude, transaction_normale):
        """Une transaction normale ne doit pas être bloquée"""
        X    = self._preparer_features(transaction_normale, encoder_fraude)
        pred = modele_fraude.predict(X)[0]
        assert pred == 0, "❌ Transaction normale bloquée !"

    def test_probabilite_fraude_elevee(
            self, modele_fraude, encoder_fraude, transaction_suspecte):
        """La probabilité de fraude doit être > 80% pour transaction suspecte"""
        X    = self._preparer_features(transaction_suspecte, encoder_fraude)
        prob = modele_fraude.predict_proba(X)[0]
        assert prob[1] >= 0.80, \
            f"❌ Probabilité fraude trop faible : {prob[1]*100:.1f}%"

    def test_types_transaction_valides(self, modele_fraude, encoder_fraude):
        """Tous les types de transaction valides doivent fonctionner"""
        types = ["depot", "retrait", "transfert", "paiement"]
        for t in types:
            tx = {
                "montant": 100_000,
                "heure_transaction": 10,
                "nb_transactions_jour": 2,
                "distance_km": 5,
                "nouveau_destinataire": 0,
                "echecs_recents": 0,
                "type_transaction": t,
            }
            X    = self._preparer_features(tx, encoder_fraude)
            pred = modele_fraude.predict(X)[0]
            assert pred in [0, 1], f"❌ Erreur pour type : {t}"

# ============================================
# LANCEMENT DIRECT
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])