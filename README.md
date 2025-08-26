# 🚕 Taxi Driver - FastAPI Reinforcement Learning

Nouvelle implémentation de l'API d'apprentissage par renforcement utilisant FastAPI, avec une architecture extensible pour intégrer facilement de nouveaux algorithmes.

## 🎯 Objectif

Reproduire la logique de l'API Python originale en se concentrant sur **SARSA** tout en gardant une architecture qui permet d'intégrer facilement d'autres algorithmes (Q-Learning, Monte Carlo, etc.) dans le futur.

## 🏗️ Architecture

```
taxi-driver/
├── main.py                 # Point d'entrée FastAPI
├── requirements.txt        # Dépendances Python
├── app/
│   ├── __init__.py
│   ├── schemas/           # Modèles Pydantic
│   │   ├── __init__.py
│   │   ├── common.py      # Paramètres communs
│   │   └── sarsa.py       # Paramètres SARSA
│   └── services/          # Logique métier
│       ├── __init__.py
│       ├── base_agent.py  # Classe de base pour les agents
│       └── sarsa.py       # Implémentation SARSA
├── assets/                # Images générées
└── models/                # Modèles sauvegardés
```

## 🚀 Installation et lancement

### 1. Installation des dépendances

```bash
cd taxi-driver
pip install -r requirements.txt
```

### 2. Lancement de l'API

```bash
python main.py
```

L'API sera disponible sur `http://localhost:8000`

### 3. Documentation interactive

- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

## 📊 Endpoints disponibles

### SARSA

- **POST** `/sarsa` - Entraînement SARSA avec paramètres personnalisés ou optimisés

### Utilitaires

- **GET** `/` - Page d'accueil
- **GET** `/health` - Vérification de l'état de l'API

## 🎮 Utilisation

### Exemple d'appel SARSA avec paramètres optimisés

```bash
curl -X POST "http://localhost:8000/sarsa" \
     -H "Content-Type: application/json" \
     -d '{
       "mode": "optimized",
       "test_episodes": 250
     }'
```

### Exemple d'appel SARSA avec paramètres personnalisés

```bash
curl -X POST "http://localhost:8000/sarsa" \
     -H "Content-Type: application/json" \
     -d '{
       "mode": "user",
       "alpha": 0.1,
       "gamma": 0.99,
       "eps": 1.0,
       "eps_decay": 0.995,
       "eps_min": 0.01,
       "training_runs": 1000,
       "maxStepsPerEpisode": 200,
       "test_episodes": 100
     }'
```

## 🔧 Paramètres SARSA

### Mode "optimized"

Utilise les paramètres validés expérimentalement :

- **alpha**: 0.12
- **gamma**: 0.99
- **eps**: 1.0
- **eps_decay**: 0.9995
- **eps_min**: 0.001
- **training_runs**: 6000
- **test_episodes**: 250

### Mode "user"

Permet de personnaliser tous les paramètres selon vos besoins.

## 📈 Fonctionnalités

### ✅ Implémenté

- **SARSA** avec métriques étendues
- **Paramètres optimisés** validés expérimentalement
- **Génération de graphiques** (6 graphiques différents)
- **Métriques système** (CPU, RAM)
- **Comparaison avec Brute Force**
- **Sauvegarde des modèles**
- **Architecture extensible** pour futurs algorithmes

### 🔮 Extensibilité future

L'architecture permet d'ajouter facilement :

- **Q-Learning**
- **Monte Carlo**
- **Deep Q-Learning**
- **K-Learning**
- **Autres algorithmes de RL**

## 🎯 Résultats attendus

Avec les paramètres optimisés, SARSA devrait atteindre :

- **Taux de succès** : ~100%
- **Nombre moyen de pas** : ~13.1
- **Amélioration vs Brute Force** : >80%

## 📁 Structure des résultats

Chaque exécution génère :

- **Images** : 6 graphiques de performance
- **Modèle** : Fichier pickle avec la Q-table
- **Rapport JSON** : Statistiques détaillées
- **Run ID unique** : Pour identifier chaque exécution

## 🔄 Différences avec l'API originale

### ✅ Améliorations

- **FastAPI** au lieu de Flask
- **Architecture modulaire** et extensible
- **Validation automatique** des paramètres
- **Documentation interactive** intégrée
- **Gestion d'erreurs** améliorée

### 🎯 Conservation

- **Logique SARSA** identique
- **Paramètres optimisés** conservés
- **Métriques et graphiques** identiques
- **Performance** équivalente

## 🚀 Prochaines étapes

1. **Tests unitaires** et d'intégration
2. **Intégration d'autres algorithmes** (Q-Learning, Monte Carlo)
3. **Interface web** pour visualiser les résultats
4. **Base de données** pour sauvegarder l'historique
5. **Authentification** et gestion des utilisateurs
