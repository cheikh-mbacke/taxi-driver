#!/bin/bash

# Script de démarrage rapide pour WSL Debian
# Optimisé pour un démarrage plus rapide

set -e

echo "🚀 Démarrage rapide des services..."

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

# Arrêter les services existants
echo "🛑 Arrêt des services existants..."
docker compose -f "$COMPOSE_FILE" down 2>/dev/null || true

# Nettoyer les conteneurs arrêtés
echo "🧹 Nettoyage des conteneurs..."
docker container prune -f 2>/dev/null || true

# Optimisations WSL et BuildKit
echo "⚡ Optimisations WSL et BuildKit..."
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_DEFAULT_PLATFORM=linux/amd64

# Démarrer les services en mode détaché avec BuildKit (sans rebuild forcé)
echo "▶️ Démarrage des services avec BuildKit..."
DOCKER_BUILDKIT=1 docker compose -f "$COMPOSE_FILE" up -d

# Attendre et vérifier le statut
echo "⏳ Attente du démarrage..."
sleep 3

echo "📊 Statut des services:"
docker compose -f "$COMPOSE_FILE" ps

# Instructions pour le frontend
echo ""
echo "🌐 Frontend (démarrer manuellement):"
echo "  cd frontend && npm install && npm run dev"

echo ""
echo "✅ Services démarrés!"
echo "🔧 API: http://localhost:8000"
echo "📚 Documentation API: http://localhost:8000/docs"
echo ""
echo "📋 Commandes utiles:"
echo "  Voir les logs: docker compose -f $COMPOSE_FILE logs -f"
echo "  Arrêter: docker compose -f $COMPOSE_FILE down"
echo "  Rebuild complet: ./start-rebuild.sh"
