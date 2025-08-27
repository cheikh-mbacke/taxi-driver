# 🚕 Taxi Driver - Reinforcement Learning API

API d'apprentissage par renforcement avec PostgreSQL pour l'environnement Taxi-v3.

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.11+
- Node.js 18+ (pour le frontend)
- Docker et Docker Compose
- PostgreSQL (optionnel, inclus dans Docker)

### Installation

```bash
# Cloner le projet
git clone <repository-url>
cd taxi-driver

# Démarrer l'API et la base de données
./start-dev.sh

# Démarrer le frontend (dans un autre terminal)
./start-frontend.sh
```

### Accès

- **Frontend** : http://localhost:3000
- **API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Base de données** : localhost:5432

## 📁 Structure du Projet

```
taxi-driver/
├── app/                    # Application principale
│   ├── api/               # API FastAPI
│   ├── ml/                # Modules ML/RL
│   └── utils/             # Utilitaires
├── infrastructure/         # Configuration infrastructure
├── tests/                 # Tests
├── docs/                  # Documentation
├── scripts/               # Scripts utilitaires
└── config/                # Configuration
```

## 🧪 Tests

```bash
# Tous les tests
make test

# Tests unitaires
make test-unit

# Tests d'intégration
make test-integration
```

## 🛠️ Développement

```bash
# Formater le code
make format

# Vérifier le code
make lint

# Nettoyer
make clean
```

## 📚 Documentation

- [Architecture](docs/architecture/)
- [API](docs/api/)
- [Déploiement](docs/deployment/)

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
