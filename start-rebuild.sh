#!/bin/bash

# Script de rebuild complet des services
# Utilise quand on veut forcer la reconstruction des images

set -e

echo "🔨 Rebuild complet des services..."

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

# Rebuild complet avec cache vidé
echo "🧹 Nettoyage du cache Docker..."
docker builder prune -f

echo "🔨 Rebuild complet des images..."
DOCKER_BUILDKIT=1 docker compose -f "$COMPOSE_FILE" build --no-cache

echo "▶️ Démarrage des services..."
DOCKER_BUILDKIT=1 docker compose -f "$COMPOSE_FILE" up -d

echo "📊 Statut des services:"
docker compose -f "$COMPOSE_FILE" ps

echo ""
echo "✅ Rebuild et démarrage terminés!"
echo "🔧 API: http://localhost:8000"
