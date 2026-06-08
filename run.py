# ============================================
# SmartFlow PME - Lanceur Principal
# ============================================

import os
import sys
import subprocess
import time

def titre(texte):
    print(f"\n{'='*55}")
    print(f"  {texte}")
    print(f"{'='*55}")

def etape(texte):
    print(f"\n⏳ {texte}...")

def succes(texte):
    print(f"✅ {texte}")

def erreur(texte):
    print(f"❌ {texte}")

# ============================================
# ÉTAPE 1 - Entraîner les modèles IA
# ============================================

def entrainer_modeles():
    titre("ÉTAPE 1 — Entraînement des modèles IA")

    modeles = [
        ("Scoring Crédit",     "ai_models/train_credit.py"),
        ("Détection Fraude",   "ai_models/train_fraud.py"),
        ("Optimisation",       "ai_models/optimisation.py"),
    ]

    for nom, script in modeles:
        etape(f"Entraînement : {nom}")
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            succes(f"{nom} entraîné avec succès !")
        else:
            erreur(f"Erreur sur {nom}")
            print(result.stderr[-500:])

# ============================================
# ÉTAPE 2 - Lancer les modules d'automatisation
# ============================================

def lancer_automatisation():
    titre("ÉTAPE 2 — Modules d'automatisation")

    modules = [
        ("Alertes Trésorerie", "ai_models/alertes.py"),
        ("Relances Clients",   "ai_models/relances.py"),
        ("Rapport Financier",  "ai_models/rapports.py"),
    ]

    for nom, script in modules:
        etape(f"Lancement : {nom}")
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            succes(f"{nom} exécuté !")
        else:
            erreur(f"Erreur sur {nom}")
            print(result.stderr[-500:])

# ============================================
# ÉTAPE 3 - Lancer les tests
# ============================================

def lancer_tests():
    titre("ÉTAPE 3 — Tests unitaires")

    etape("Lancement des tests")
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/test_models.py", "-v", "--tb=short"],
        capture_output=False, text=True
    )
    if result.returncode == 0:
        succes("Tous les tests passés !")
    else:
        erreur("Certains tests ont échoué !")

# ============================================
# ÉTAPE 4 - Lancer l'API
# ============================================

def lancer_api():
    titre("ÉTAPE 4 — Lancement de l'API FastAPI")

    print("\n🚀 Démarrage du serveur...")
    print("📖 Documentation : http://127.0.0.1:8000/docs")
    print("🔴 Pour arrêter  : Ctrl + C\n")

    os.system(
        f"{sys.executable} -m uvicorn backend.main:app --reload"
    )

# ============================================
# MENU PRINCIPAL
# ============================================

def menu():
    print("""
╔══════════════════════════════════════════════╗
║       SmartFlow PME — Lanceur Principal      ║
║   Système IA pour PME Africaines — STIC'26   ║
╠══════════════════════════════════════════════╣
║  1. Entraîner les modèles IA                 ║
║  2. Lancer l'automatisation                  ║
║  3. Lancer les tests                         ║
║  4. Lancer l'API                             ║
║  5. TOUT lancer (1+2+3+4)                    ║
║  0. Quitter                                  ║
╚══════════════════════════════════════════════╝
    """)

    choix = input("Votre choix : ").strip()

    if choix == "1":
        entrainer_modeles()
        menu()
    elif choix == "2":
        lancer_automatisation()
        menu()
    elif choix == "3":
        lancer_tests()
        menu()
    elif choix == "4":
        lancer_api()
    elif choix == "5":
        entrainer_modeles()
        lancer_tests()
        lancer_api()
    elif choix == "0":
        print("\n👋 Au revoir !\n")
        sys.exit(0)
    else:
        print("❌ Choix invalide !")
        menu()

# ============================================
# LANCEMENT
# ============================================

if __name__ == "__main__":
    menu()