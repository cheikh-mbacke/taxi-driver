# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Installer les dépendances système pour la compilation
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier seulement les requirements
COPY requirements.txt .

# Mettre à jour pip et activer le cache
RUN pip install --upgrade pip && \
    pip install --user \
    --timeout 300 \
    -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances runtime
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les packages installés depuis le builder
COPY --from=builder /root/.local /root/.local

# Ajouter le PATH et PYTHONPATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Copier seulement les fichiers nécessaires
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY config/ ./config/

# Créer les dossiers nécessaires
RUN mkdir -p data/results data/models data/logs

# Exposer le port
EXPOSE 8000

# Rendre le script d'initialisation exécutable
RUN chmod +x scripts/init_app.py

# Script de démarrage
COPY scripts/start.sh /start.sh
RUN chmod +x /start.sh

# Commande de démarrage
CMD ["/start.sh"]
