import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Configuration de la base de données
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://taxi_user:taxi_password@localhost:5432/taxi_driver"
)

# Création du moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=False  # Mettre à True pour voir les requêtes SQL
)

# Création de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

def get_db():
    """Dependency pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialise la base de données avec les tables"""
    Base.metadata.create_all(bind=engine)
    
    # Créer un utilisateur par défaut si nécessaire
    db = SessionLocal()
    try:
        from app.api.models import User
        import uuid
        
        default_user_id = "00000000-0000-0000-0000-000000000001"  # UUID fixe pour l'utilisateur par défaut
        default_user = db.query(User).filter(User.user_id == default_user_id).first()
        if not default_user:
            default_user = User(
                user_id=default_user_id,
                username="default_user",
                email="default@taxi-driver.com"
            )
            db.add(default_user)
            db.commit()
            print("✅ Utilisateur par défaut créé")
    except Exception as e:
        print(f"⚠️ Erreur lors de la création de l'utilisateur par défaut: {e}")
    finally:
        db.close()
