#!/bin/bash

# Script de démarrage pour l'application Taxi Driver

echo "🚕 Démarrage de Taxi Driver API..."

# Initialiser la base de données
echo "🗄️ Initialisation de la base de données..."
python scripts/init_app.py

# Vérifier si l'initialisation a réussi
if [ $? -eq 0 ]; then
    echo "✅ Base de données initialisée avec succès"
    
    # Démarrer l'application FastAPI
    echo "🚀 Démarrage de l'API FastAPI..."
    
    # Vérifier si on est en mode développement
    if [ "$DEBUG" = "true" ] && [ "$RELOAD" = "true" ]; then
        echo "🔄 Mode développement avec reload activé"
        exec uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app/app
    else
        echo "🏭 Mode production"
        exec uvicorn app.api.main:app --host 0.0.0.0 --port 8000
    fi
else
    echo "❌ Erreur lors de l'initialisation de la base de données"
    exit 1
fi
