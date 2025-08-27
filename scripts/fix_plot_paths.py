#!/usr/bin/env python3
"""
Script pour corriger les chemins des plots dans la base de données.
Remplace /assets/images/ par /assets/ dans les chemins stockés.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.api.database import get_db
from app.api.models import TrainingRun

def fix_plot_paths():
    """Corrige les chemins des plots dans la base de données"""
    
    # Connexion à la base de données
    engine = create_engine("postgresql://taxi_user:taxi_password@localhost:5432/taxi_driver")
    
    try:
        with engine.connect() as conn:
            # Récupérer tous les runs qui ont des plots avec /assets/images/
            query = text("""
                SELECT run_id, plots 
                FROM training_runs 
                WHERE plots IS NOT NULL 
                AND plots::text LIKE '%/assets/images/%'
            """)
            
            result = conn.execute(query)
            runs_to_update = result.fetchall()
            
            print(f"🔍 Trouvé {len(runs_to_update)} runs avec des chemins incorrects")
            
            if not runs_to_update:
                print("✅ Aucun chemin à corriger")
                return
            
            # Mettre à jour chaque run
            for run_id, plots in runs_to_update:
                if plots:
                    # Corriger les chemins
                    corrected_plots = []
                    for plot_path in plots:
                        corrected_path = plot_path.replace('/assets/images/', '/assets/')
                        corrected_plots.append(corrected_path)
                        print(f"  📝 {plot_path} → {corrected_path}")
                    
                    # Mettre à jour en base
                    update_query = text("""
                        UPDATE training_runs 
                        SET plots = :plots 
                        WHERE run_id = :run_id
                    """)
                    
                    conn.execute(update_query, {
                        'plots': corrected_plots,
                        'run_id': run_id
                    })
                    
                    print(f"✅ Run {run_id} mis à jour")
            
            # Valider les changements
            conn.commit()
            print(f"🎉 {len(runs_to_update)} runs mis à jour avec succès")
            
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
        raise

if __name__ == "__main__":
    print("🚀 Début de la correction des chemins des plots...")
    fix_plot_paths()
    print("✅ Script terminé")
