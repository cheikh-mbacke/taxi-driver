# 🗄️ Taxi Driver - Base de Données PostgreSQL

## 📊 Nouveautés v2.0.0

Cette version ajoute une **base de données PostgreSQL** complète avec **JSONB** pour stocker et analyser tous les résultats d'entraînement.

## 🏗️ Architecture avec Base de Données

```
taxi-driver/
├── docker-compose.yml          # PostgreSQL + API
├── init-db.sql                 # Script d'initialisation DB
├── fastapi/
│   ├── app/
│   │   ├── database.py         # Configuration SQLAlchemy
│   │   ├── models.py           # Modèles SQLAlchemy
│   │   ├── schemas/
│   │   │   └── database.py     # Schémas Pydantic pour DB
│   │   ├── services/
│   │   │   └── database_service.py  # Service DB
│   │   └── routes/
│   │       └── database_routes.py    # Routes DB
│   ├── init_app.py             # Script d'initialisation
│   └── start.sh                # Script de démarrage
```

## 🚀 Démarrage Rapide

### 1. Lancer avec Docker Compose

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f taxi-driver-api
```

### 2. Accéder à l'API

- **API** : http://localhost:8000
- **Documentation** : http://localhost:8000/docs
- **Base de données** : localhost:5432

## 📊 Tables de la Base de Données

### 1. `training_runs` - Runs d'entraînement

```sql
CREATE TABLE training_runs (
    run_id UUID PRIMARY KEY,
    algorithm VARCHAR(50),
    params JSONB,              -- Paramètres d'entraînement
    training_metrics JSONB,     -- Métriques d'entraînement
    test_metrics JSONB,         -- Métriques de test
    system_metrics JSONB,       -- Métriques système
    learning_stability JSONB,   -- Stabilité d'apprentissage
    brute_force_metrics JSONB,  -- Métriques brute force
    improvement_metrics JSONB,  -- Métriques d'amélioration
    model_path VARCHAR(500),    -- Chemin du modèle
    plots JSONB,               -- Chemins des graphiques
    execution_time FLOAT,       -- Temps d'exécution
    created_at TIMESTAMP
);
```

### 2. `saved_models` - Modèles sauvegardés

```sql
CREATE TABLE saved_models (
    model_id UUID PRIMARY KEY,
    run_id UUID REFERENCES training_runs,
    model_name VARCHAR(100),
    model_path VARCHAR(500),
    model_size BIGINT,
    model_metadata JSONB,
    created_at TIMESTAMP
);
```

### 3. `run_annotations` - Annotations et commentaires

```sql
CREATE TABLE run_annotations (
    annotation_id UUID PRIMARY KEY,
    run_id UUID REFERENCES training_runs,
    annotation TEXT,
    tags TEXT[],               -- Array de tags
    created_at TIMESTAMP
);
```

### 4. `users` - Utilisateurs (pour future extensibilité)

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(255),
    created_at TIMESTAMP
);
```

## 🔌 Nouveaux Endpoints API

### 📊 Gestion des Runs

#### Liste des runs

```bash
GET /database/runs?skip=0&limit=100&algorithm=sarsa
```

#### Détails d'un run

```bash
GET /database/runs/{run_id}
```

#### Meilleurs runs

```bash
GET /database/runs/best?algorithm=sarsa&limit=10
```

#### Statistiques globales

```bash
GET /database/statistics
```

### 🔍 Recherche et Filtrage

#### Recherche par paramètres

```bash
GET /database/runs/search/params?alpha=0.1&gamma=0.99
```

#### Comparaison de runs

```bash
POST /database/runs/compare
{
    "run_ids": ["uuid1", "uuid2", "uuid3"]
}
```

### 📝 Annotations

#### Ajouter une annotation

```bash
POST /database/runs/{run_id}/annotations
{
    "annotation": "Excellent résultat avec ces paramètres",
    "tags": ["optimized", "best_performance"]
}
```

#### Lister les annotations

```bash
GET /database/runs/{run_id}/annotations
```

### 🗑️ Gestion

#### Supprimer un run

```bash
DELETE /database/runs/{run_id}
```

#### Santé de la base

```bash
GET /database/health
```

## 📈 Exemples d'Utilisation

### 1. Entraînement SARSA avec sauvegarde automatique

```bash
curl -X POST "http://localhost:8000/sarsa" \
     -H "Content-Type: application/json" \
     -d '{
       "mode": "optimized",
       "test_episodes": 250
     }'
```

**Résultat** : Le run est automatiquement sauvegardé en base avec toutes ses métriques.

### 2. Récupérer l'historique des runs

```bash
curl "http://localhost:8000/database/runs?limit=10"
```

### 3. Comparer les meilleurs runs

```bash
# Récupérer les 5 meilleurs runs
curl "http://localhost:8000/database/runs/best?limit=5"

# Comparer 3 runs spécifiques
curl -X POST "http://localhost:8000/database/runs/compare" \
     -H "Content-Type: application/json" \
     -d '{
       "run_ids": ["uuid1", "uuid2", "uuid3"]
     }'
```

### 4. Rechercher des runs par paramètres

```bash
curl "http://localhost:8000/database/runs/search/params?alpha=0.12&training_runs=6000"
```

## 🔧 Requêtes SQL Avancées

### Statistiques par algorithme

```sql
SELECT
    algorithm,
    COUNT(*) as total_runs,
    AVG((test_metrics->>'success_rate')::FLOAT) as avg_success,
    AVG((test_metrics->>'avg_steps')::FLOAT) as avg_steps
FROM training_runs
WHERE status = 'completed'
GROUP BY algorithm;
```

### Évolution des performances dans le temps

```sql
SELECT
    DATE_TRUNC('day', created_at) as day,
    AVG((test_metrics->>'success_rate')::FLOAT) as avg_success
FROM training_runs
GROUP BY day
ORDER BY day;
```

### Recherche de paramètres optimaux

```sql
SELECT
    params->>'alpha' as alpha,
    params->>'gamma' as gamma,
    test_metrics->>'success_rate' as success_rate
FROM training_runs
WHERE (test_metrics->>'success_rate')::FLOAT > 0.9
ORDER BY (test_metrics->>'avg_steps')::FLOAT ASC;
```

## 🎯 Avantages de la Base de Données

### ✅ Historique Complet

- Tous les runs sont sauvegardés automatiquement
- Pas de perte de données
- Traçabilité complète

### ✅ Recherche Avancée

- Filtrage par paramètres
- Recherche par performance
- Comparaisons multiples

### ✅ Analytics

- Statistiques globales
- Tendances temporelles
- Identification des meilleurs paramètres

### ✅ Collaboration

- Annotations et commentaires
- Partage de résultats
- Système multi-utilisateurs (futur)

### ✅ Reprise d'Entraînement

- Sauvegarde automatique des états
- Reprise en cas d'interruption
- Historique des modèles

## 🔮 Fonctionnalités Futures

- **Interface Web** pour visualiser les résultats
- **Système d'authentification** complet
- **Export/Import** de modèles
- **Notifications** en temps réel
- **API GraphQL** pour requêtes complexes
- **Machine Learning** pour recommandations automatiques

## 🛠️ Maintenance

### Sauvegarde de la base

```bash
docker-compose exec postgres pg_dump -U taxi_user taxi_driver > backup.sql
```

### Restauration

```bash
docker-compose exec -T postgres psql -U taxi_user taxi_driver < backup.sql
```

### Nettoyage des anciens runs

```sql
DELETE FROM training_runs
WHERE created_at < NOW() - INTERVAL '30 days';
```

## 📊 Métriques Stockées

Chaque run sauvegarde automatiquement :

- **Paramètres d'entraînement** (alpha, gamma, epsilon, etc.)
- **Métriques d'entraînement** (récompenses, pas, erreurs TD)
- **Métriques de test** (taux de succès, pas moyens)
- **Métriques système** (CPU, RAM, temps d'exécution)
- **Stabilité d'apprentissage** (variance Q-table, convergence)
- **Comparaison brute force** (amélioration, efficacité)
- **Chemins des fichiers** (modèles, graphiques)

Cette architecture permet une **analyse complète** et **historique** de tous les entraînements !
