#!/usr/bin/env python3
"""
Script d'initialisation de l'application Taxi Driver
Initialise la base de données et crée les tables nécessaires
"""

import os
import time
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

def wait_for_database():
    """Attend que la base de données soit disponible"""
    print("🔄 Attente de la base de données PostgreSQL...")
    
    max_attempts = 15  # Réduit de 30 à 15
    attempt = 0
    
    while attempt < max_attempts:
        try:
            from app.api.database import engine
            from sqlalchemy import text
            
            # Test de connexion avec la syntaxe SQLAlchemy 2.0
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                conn.commit()
            print("✅ Base de données PostgreSQL connectée avec succès!")
            return True
        except Exception as e:
            attempt += 1
            print(f"⏳ Tentative {attempt}/{max_attempts} - Base de données non disponible: {e}")
            time.sleep(1)  # Réduit de 2s à 1s
    
    print("❌ Impossible de se connecter à la base de données après 15 tentatives")
    return False

def init_database():
    """Initialise la base de données"""
    try:
        from app.api.database import engine
        from app.api.models import Base
        
        print("🗄️ Initialisation de la base de données...")
        
        # Créer toutes les tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tables créées avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
        return False

def create_default_user():
    """Crée un utilisateur par défaut si nécessaire"""
    try:
        from app.api.database import SessionLocal
        from app.api.models import User
        
        db = SessionLocal()
        
        # Vérifier si l'utilisateur admin existe déjà
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@taxi-driver.local"
            )
            db.add(admin_user)
            db.commit()
            print("✅ Utilisateur admin créé avec succès!")
        else:
            print("ℹ️ Utilisateur admin existe déjà")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur admin: {e}")
        return False

def main():
    """Fonction principale d'initialisation"""
    print("🚀 Initialisation de l'application Taxi Driver...")
    
    # Attendre la base de données
    if not wait_for_database():
        sys.exit(1)
    
    # Initialiser la base de données
    if not init_database():
        sys.exit(1)
    
    # Créer l'utilisateur par défaut
    if not create_default_user():
        sys.exit(1)
    
    print("🎉 Initialisation terminée avec succès!")
    print("📊 L'API est prête à être utilisée")
    print("🔗 Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
