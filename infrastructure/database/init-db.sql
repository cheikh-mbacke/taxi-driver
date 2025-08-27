-- Initialisation de la base de données Taxi Driver
-- Extension pour JSONB
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table des utilisateurs (pour future extensibilité)
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des runs d'entraînement
CREATE TABLE IF NOT EXISTS training_runs (
    run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    algorithm VARCHAR(50) NOT NULL,
    params JSONB NOT NULL,
    training_metrics JSONB,
    test_metrics JSONB,
    system_metrics JSONB,
    learning_stability JSONB,
    brute_force_metrics JSONB,
    improvement_metrics JSONB,
    model_path VARCHAR(500),
    plots JSONB, -- Array des chemins vers les graphiques
    execution_time FLOAT,
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des modèles sauvegardés
CREATE TABLE IF NOT EXISTS saved_models (
    model_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES training_runs(run_id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,
    model_path VARCHAR(500) NOT NULL,
    model_size BIGINT,
    model_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des annotations et commentaires
CREATE TABLE IF NOT EXISTS run_annotations (
    annotation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES training_runs(run_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    annotation TEXT NOT NULL,
    tags TEXT[], -- Array de tags
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_training_runs_algorithm ON training_runs(algorithm);
CREATE INDEX IF NOT EXISTS idx_training_runs_created_at ON training_runs(created_at);
CREATE INDEX IF NOT EXISTS idx_training_runs_user_id ON training_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_training_runs_params ON training_runs USING GIN(params);
CREATE INDEX IF NOT EXISTS idx_training_runs_test_metrics ON training_runs USING GIN(test_metrics);

-- Index pour les annotations
CREATE INDEX IF NOT EXISTS idx_run_annotations_run_id ON run_annotations(run_id);
CREATE INDEX IF NOT EXISTS idx_run_annotations_tags ON run_annotations USING GIN(tags);

-- Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour updated_at
CREATE TRIGGER update_training_runs_updated_at 
    BEFORE UPDATE ON training_runs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Vue pour les statistiques globales
CREATE OR REPLACE VIEW training_statistics AS
SELECT 
    algorithm,
    COUNT(*) as total_runs,
    AVG((test_metrics->>'success_rate')::FLOAT) as avg_success_rate,
    AVG((test_metrics->>'avg_steps')::FLOAT) as avg_steps,
    AVG(execution_time) as avg_execution_time,
    MIN(created_at) as first_run,
    MAX(created_at) as last_run
FROM training_runs 
WHERE status = 'completed'
GROUP BY algorithm;

-- Fonction pour obtenir les meilleurs runs
CREATE OR REPLACE FUNCTION get_best_runs(
    p_algorithm VARCHAR DEFAULT NULL,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    run_id UUID,
    algorithm VARCHAR,
    success_rate FLOAT,
    avg_steps FLOAT,
    execution_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        tr.run_id,
        tr.algorithm,
        (tr.test_metrics->>'success_rate')::FLOAT as success_rate,
        (tr.test_metrics->>'avg_steps')::FLOAT as avg_steps,
        tr.execution_time,
        tr.created_at
    FROM training_runs tr
    WHERE tr.status = 'completed'
      AND (p_algorithm IS NULL OR tr.algorithm = p_algorithm)
    ORDER BY (tr.test_metrics->>'success_rate')::FLOAT DESC,
             (tr.test_metrics->>'avg_steps')::FLOAT ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Insertion d'un utilisateur par défaut (admin)
INSERT INTO users (username, email) 
VALUES ('admin', 'admin@taxi-driver.local')
ON CONFLICT (username) DO NOTHING;

-- Commentaires pour la documentation
COMMENT ON TABLE training_runs IS 'Stockage des résultats d''entraînement des algorithmes de RL';
COMMENT ON TABLE saved_models IS 'Métadonnées des modèles sauvegardés';
COMMENT ON TABLE run_annotations IS 'Annotations et commentaires sur les runs';
COMMENT ON TABLE users IS 'Utilisateurs du système (pour future extensibilité)';
