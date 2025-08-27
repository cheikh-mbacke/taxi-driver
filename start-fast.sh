#!/bin/bash

# Script de démarrage ultra-rapide
# Démarre les services progressivement pour éviter les blocages

set -e

echo "⚡ Démarrage ultra-rapide des services..."

# Variables
COMPOSE_FILE="infrastructure/docker/docker-compose.yml"

# Vérifier que le fichier existe
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ Fichier docker-compose.yml non trouvé!"
    exit 1
fi

# Vérifier que Docker est démarré
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker n'est pas démarré. Démarrez Docker Desktop d'abord."
    exit 1
fi

# Optimisations WSL et BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_DEFAULT_PLATFORM=linux/amd64

# Arrêter les services existants
echo "🛑 Arrêt des services existants..."
docker compose -f "$COMPOSE_FILE" down 2>/dev/null || true

# Nettoyer les conteneurs arrêtés
echo "🧹 Nettoyage des conteneurs..."
docker container prune -f 2>/dev/null || true

# Démarrage progressif ultra-rapide
echo "🚀 Démarrage progressif..."

# 1. Démarrer PostgreSQL en premier
echo "🗄️ Démarrage PostgreSQL..."
docker compose -f "$COMPOSE_FILE" up -d postgres

# 2. Attendre seulement 5 secondes
echo "⏳ Attente PostgreSQL (5s)..."
sleep 5

# 3. Démarrer l'API en parallèle
echo "🔧 Démarrage API..."
docker compose -f "$COMPOSE_FILE" up -d taxi-driver-api

# 4. Attendre seulement 3 secondes
echo "⏳ Attente API (3s)..."
sleep 3



# 6. Vérifier le statut
echo "📊 Statut des services:"
docker compose -f "$COMPOSE_FILE" ps

echo ""
echo "✅ Services démarrés en mode ultra-rapide!"
echo "🔧 API: http://localhost:8000"
echo "📚 Documentation API: http://localhost:8000/docs"
echo ""
echo "🌐 Frontend (démarrer manuellement):"
echo "  cd frontend && npm install && npm run dev"
echo ""
echo "📋 Commandes utiles:"
echo "  Voir les logs: docker compose -f $COMPOSE_FILE logs -f"
echo "  Arrêter: docker compose -f $COMPOSE_FILE down"
echo "  Rebuild: docker compose -f $COMPOSE_FILE build --no-cache"
