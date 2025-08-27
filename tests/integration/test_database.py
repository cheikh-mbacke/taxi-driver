#!/usr/bin/env python3
"""
Script de test pour vérifier le bon fonctionnement de la base de données
"""

import requests
import json
import time
from uuid import UUID

BASE_URL = "http://localhost:8000"

def test_health():
    """Test de santé de l'API"""
    print("🔍 Test de santé de l'API...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API en ligne")
            return True
        else:
            print(f"❌ API hors ligne: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_database_health():
    """Test de santé de la base de données"""
    print("🗄️ Test de santé de la base de données...")
    try:
        response = requests.get(f"{BASE_URL}/database/health")
        if response.status_code == 200:
            print("✅ Base de données connectée")
            return True
        else:
            print(f"❌ Base de données hors ligne: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion DB: {e}")
        return False

def test_sarsa_training():
    """Test d'un entraînement SARSA"""
    print("🚕 Test d'entraînement SARSA...")
    try:
        payload = {
            "mode": "user",
            "alpha": 0.1,
            "gamma": 0.99,
            "eps": 1.0,
            "eps_decay": 0.995,
            "eps_min": 0.01,
            "training_runs": 100,  # Petit test
            "maxStepsPerEpisode": 200,
            "test_episodes": 50
        }
        
        response = requests.post(f"{BASE_URL}/sarsa", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Entraînement réussi - Run ID: {result.get('run_id')}")
            return result.get('run_id')
        else:
            print(f"❌ Erreur d'entraînement: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur d'entraînement: {e}")
        return None

def test_get_runs():
    """Test de récupération des runs"""
    print("📊 Test de récupération des runs...")
    try:
        response = requests.get(f"{BASE_URL}/database/runs?limit=5")
        if response.status_code == 200:
            runs = response.json()
            print(f"✅ {len(runs)} runs récupérés")
            return runs
        else:
            print(f"❌ Erreur de récupération: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erreur de récupération: {e}")
        return []

def test_get_statistics():
    """Test de récupération des statistiques"""
    print("📈 Test de récupération des statistiques...")
    try:
        response = requests.get(f"{BASE_URL}/database/statistics")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistiques récupérées - Total runs: {stats.get('total_runs')}")
            return stats
        else:
            print(f"❌ Erreur de statistiques: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur de statistiques: {e}")
        return None

def test_get_best_runs():
    """Test de récupération des meilleurs runs"""
    print("🏆 Test de récupération des meilleurs runs...")
    try:
        response = requests.get(f"{BASE_URL}/database/runs/best?limit=3")
        if response.status_code == 200:
            best_runs = response.json()
            print(f"✅ {len(best_runs)} meilleurs runs récupérés")
            return best_runs
        else:
            print(f"❌ Erreur des meilleurs runs: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erreur des meilleurs runs: {e}")
        return []

def test_add_annotation(run_id):
    """Test d'ajout d'annotation"""
    print(f"📝 Test d'ajout d'annotation pour le run {run_id}...")
    try:
        payload = {
            "annotation": "Test d'annotation automatique",
            "tags": ["test", "automated"]
        }
        
        response = requests.post(f"{BASE_URL}/database/runs/{run_id}/annotations", json=payload)
        if response.status_code == 200:
            annotation = response.json()
            print(f"✅ Annotation ajoutée - ID: {annotation.get('annotation_id')}")
            return True
        else:
            print(f"❌ Erreur d'annotation: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur d'annotation: {e}")
        return False

def test_search_runs():
    """Test de recherche de runs"""
    print("🔍 Test de recherche de runs...")
    try:
        response = requests.get(f"{BASE_URL}/database/runs/search/params?alpha=0.1&training_runs=100")
        if response.status_code == 200:
            search_result = response.json()
            print(f"✅ Recherche réussie - {search_result.get('total_found')} runs trouvés")
            return True
        else:
            print(f"❌ Erreur de recherche: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de recherche: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Tests de la base de données Taxi Driver")
    print("=" * 50)
    
    # Attendre que l'API soit prête
    print("⏳ Attente de l'API...")
    time.sleep(5)
    
    # Tests de base
    if not test_health():
        print("❌ L'API n'est pas accessible")
        return
    
    if not test_database_health():
        print("❌ La base de données n'est pas accessible")
        return
    
    # Test d'entraînement
    run_id = test_sarsa_training()
    if not run_id:
        print("❌ L'entraînement a échoué")
        return
    
    # Attendre que l'entraînement soit terminé
    print("⏳ Attente de la fin de l'entraînement...")
    time.sleep(10)
    
    # Tests de récupération
    runs = test_get_runs()
    stats = test_get_statistics()
    best_runs = test_get_best_runs()
    
    # Tests d'annotations
    if run_id:
        test_add_annotation(run_id)
    
    # Test de recherche
    test_search_runs()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 Résumé des tests:")
    print(f"✅ API: {'OK' if test_health() else 'KO'}")
    print(f"✅ Base de données: {'OK' if test_database_health() else 'KO'}")
    print(f"✅ Entraînement: {'OK' if run_id else 'KO'}")
    print(f"✅ Récupération runs: {'OK' if runs else 'KO'}")
    print(f"✅ Statistiques: {'OK' if stats else 'KO'}")
    print(f"✅ Meilleurs runs: {'OK' if best_runs else 'KO'}")
    print(f"✅ Recherche: {'OK' if test_search_runs() else 'KO'}")
    
    if run_id:
        print(f"🎯 Run de test créé: {run_id}")
    
    print("\n🎉 Tests terminés!")

if __name__ == "__main__":
    main()
