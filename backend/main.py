# backend/main.py
# ============================================
# SmartFlow PME - Point d'entrée FastAPI
# Chef de Projet : OUEDRAOGO Kevin
# ============================================

from fastapi import FastAPI
from backend.database.db import engine, Base

# Importer les routes
from backend.routes import clients, transactions, credits, fraud

# Créer les tables en base
Base.metadata.create_all(bind=engine)

# Initialiser l'application
app = FastAPI(
    title="SmartFlow PME API",
    description="Système d'IA de gestion financière prédictive pour PME Africaines",
    version="1.0.0"
)

# Enregistrer les routes
app.include_router(clients.router)
app.include_router(transactions.router)
app.include_router(credits.router)
app.include_router(fraud.router)

@app.get("/")
def root():
    return {
        "message":    "✅ SmartFlow PME API opérationnelle",
        "version":    "1.0.0",
        "docs":       "/docs",
        "equipe":     [
            "OUEDRAOGO Kevin — Chef de Projet",
            "TAONDEYANDE Wendmanegda Jean-Claude — IA"
        ]
    }