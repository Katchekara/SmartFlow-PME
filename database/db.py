from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# URL de connexion SQLite (fichier smartflow.db dans la racine du projet)
DATABASE_URL = "sqlite:///./smartflow.db"

# Création du moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session locale pour gérer les transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dépendance FastAPI pour obtenir une session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
