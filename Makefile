.PHONY: help install dev test lint format clean docker-up docker-down

help: ## Afficher cette aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installer les dépendances
	pip install -r requirements.txt

install-dev: ## Installer les dépendances de développement
	pip install -r requirements-dev.txt

dev: ## Lancer en mode développement
	uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

test: ## Lancer les tests
	pytest tests/ -v

test-unit: ## Lancer les tests unitaires
	pytest tests/unit/ -v

test-integration: ## Lancer les tests d'intégration
	pytest tests/integration/ -v

lint: ## Vérifier le code avec flake8
	flake8 app/ tests/

format: ## Formater le code avec black et isort
	black app/ tests/
	isort app/ tests/

clean: ## Nettoyer les fichiers temporaires
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

docker-up: ## Démarrer les services Docker
	docker-compose -f infrastructure/docker/docker-compose.yml up -d

docker-down: ## Arrêter les services Docker
	docker-compose -f infrastructure/docker/docker-compose.yml down

docker-logs: ## Afficher les logs Docker
	docker-compose -f infrastructure/docker/docker-compose.yml logs -f

setup: install install-dev ## Configuration complète du projet
	@echo "✅ Configuration terminée!"
