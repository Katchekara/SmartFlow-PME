# 🚀 SmartFlow PME

> Système d'IA de Gestion Financière Prédictive pour PME Africaines

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![ML](https://img.shields.io/badge/ML-Scikit--learn-orange)
![Tests](https://img.shields.io/badge/Tests-17%2F17%20✅-brightgreen)
![STIC26](https://img.shields.io/badge/STIC'26-FinTech%20%26%20IA-red)

---

## 👥 Équipe

| Nom | Rôle | Formation |
|-----|------|-----------|
| **OUEDRAOGO Kevin** | Chef de Projet & Développeur Backend | L1 Systèmes d'Information et Réseaux |
| **TAONDEYANDE Wendmanegda Jean-Claude** | Responsable IA & Automatisation | L1 Systèmes d'Information et Réseaux |

---

## 🎯 Problème résolu

**34% des PME africaines** souffrent de crises de trésorerie chroniques.
Elles n'ont pas accès aux outils financiers intelligents réservés aux grandes entreprises.

**SmartFlow PME** leur donne accès à :
- Un **directeur financier IA** dans leur poche
- Des **prédictions de trésorerie** à 30 jours
- Un **scoring de crédit** basé sur leurs données réelles
- Une **détection de fraude** Mobile Money en temps réel

---

## 🤖 Modèles IA

| Modèle | Algorithme | Précision | Rôle |
|--------|-----------|-----------|------|
| Scoring Crédit | Random Forest | **98%** | Décision d'octroi de crédit |
| Détection Fraude | Random Forest | **95%+** | Détection transactions suspectes |
| Alertes Trésorerie | Prédictif | — | Prédiction crises 30 jours |

---

## 🏗️ Structure du projet
SmartFlow-PME/
├── ai_models/               # Modèles IA
│   ├── models/              # Modèles entraînés (.joblib)
│   ├── train_credit.py      # Scoring crédit (98%)
│   ├── train_fraud.py       # Détection fraude
│   ├── alertes.py           # Alertes trésorerie
│   ├── relances.py          # Relances automatiques
│   ├── rapports.py          # Rapports financiers
│   └── optimisation.py      # Optimisation modèles
├── backend/                 # API FastAPI
│   ├── main.py              # Point d'entrée
│   ├── routes/              # Endpoints
│   └── database/            # BDD SQLite
├── tests/                   # Tests unitaires
│   └── test_models.py       # 17/17 tests ✅
└── docs/                    # Documentation

---

## ⚡ Installation rapide

### 1. Cloner le projet
```bash
git clone https://github.com/Katchekara/SmartFlow-PME.git
cd SmartFlow-PME
```

### 2. Installer les dépendances
```bash
pip install -r backend/requirements.txt
```

### 3. Entraîner les modèles IA
```bash
python ai_models/train_credit.py
python ai_models/train_fraud.py
```

### 4. Lancer l'API
```bash
python -m uvicorn backend.main:app --reload
```

### 5. Accéder à la documentation
http://127.0.0.1:8000/docs

---

## 🧪 Lancer les tests

```bash
python -m pytest tests/test_models.py -v
```

**Résultat : 17/17 tests passés ✅**

---

## 🔌 Endpoints principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/clients/` | Créer un client PME |
| POST | `/credits/` | Scoring crédit IA |
| POST | `/fraud/` | Détecter une fraude |
| GET | `/fraud/alertes` | Lister les alertes |

---

## 🌍 Impact

- 🎯 **Marché cible** : 67M+ PME sous-bancarisées en Afrique
- 📈 **Croissance Mobile Money** : +34%/an en Afrique de l'Ouest
- 💰 **Économies potentielles** : -23% de pertes liées aux impayés
- 🏆 **Compétition** : Sahal Tech Innovation Challenge 2026 (STIC'26)

---

## 📄 Licence

Projet développé dans le cadre du **STIC'26** — Sahal Tech Innovation Labs, Burkina Faso 🇧🇫

