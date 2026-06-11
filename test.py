# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.db import engine, Base
from backend.routes import clients, transactions, credits, fraud, ia

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartFlow PME API",
    description="Système d'IA de gestion financière prédictive pour PME Africaines",
    version="1.0.0"
)

# ── CORS — autorise le site web à appeler l'API ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router)
app.include_router(transactions.router)
app.include_router(credits.router)
app.include_router(fraud.router)
app.include_router(ia.router)

@app.get("/")
def root():
    return {
        "message": "✅ SmartFlow PME API opérationnelle",
        "version": "1.0.0",
        "docs":    "/docs",
        "equipe":  [
            "OUEDRAOGO Kevin — Chef de Projet",
            "TAONDEYANDE Wendmanegda Jean-Claude — IA"
        ]
    }