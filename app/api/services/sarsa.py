import os
import uuid
import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import psutil
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
import gymnasium as gym
from datetime import datetime

from app.api.schemas.sarsa import SarsaParams
from app.api.schemas.database import TrainingRunCreate, SavedModelCreate
from app.api.services.base_agent import BaseAgent, BruteForceAgent

def get_system_metrics():
    """Récupère les métriques système actuelles"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_mb": memory.used / 1024 / 1024,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"⚠️ Erreur lors de la récupération des métriques système: {e}")
        return {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "memory_mb": 0.0,
            "timestamp": datetime.now().isoformat()
        }

class SarsaAgent(BaseAgent):
    """Agent SARSA (State-Action-Reward-State-Action)"""
    
    def __init__(self, env: gym.Env, alpha: float = 0.1, gamma: float = 0.99, eps: float = 1.0):
        super().__init__(env)
        self.alpha = alpha  # Taux d'apprentissage
        self.gamma = gamma  # Facteur d'actualisation
        self.eps = eps      # Paramètre d'exploration epsilon
        self.q_table = np.zeros((self.n_states, self.n_actions))
        
    def get_action(self, state: int) -> int:
        """Choisit une action selon la politique epsilon-greedy"""
        if np.random.random() < self.eps:
            return np.random.randint(self.n_actions)  # Exploration
        else:
            return np.argmax(self.q_table[state])     # Exploitation
    
    def choose_action(self, state: int) -> int:
        """Alias pour get_action pour compatibilité"""
        return self.get_action(state)
    
    def update(self, state: int, action: int, reward: float, next_state: int, next_action: int = None) -> float:
        """Met à jour la Q-table selon l'algorithme SARSA"""
        if next_action is None:
            next_action = self.get_action(next_state)
            
        current_q = self.q_table[state, action]
        next_q = self.q_table[next_state, next_action]
        td_target = reward + self.gamma * next_q
        td_error = td_target - current_q
        self.q_table[state, action] = current_q + self.alpha * td_error
        return td_error
    
    def decay_epsilon(self, eps_decay: float = 0.999, eps_min: float = 0.01) -> None:
        """Décroissance de l'epsilon pour l'exploration"""
        self.eps = max(eps_min, self.eps * eps_decay)

def train_sarsa(agent: SarsaAgent, env, episodes: int, max_steps: int = 200, 
                eps_decay: float = 0.999, eps_min: float = 0.01) -> Dict[str, Any]:
    """Entraîne l'agent SARSA"""
    
    print(f"🚀 Début de l'entraînement SARSA ({episodes} épisodes)")
    
    # Métriques de suivi
    episode_rewards = []
    episode_steps = []
    episode_successes = []
    td_errors = []
    system_metrics = []
    
    for episode in range(episodes):
        state, _ = env.reset()
        action = agent.choose_action(state)
        total_reward = 0
        steps = 0
        episode_td_errors = []
        
        # Métriques système au début de l'épisode
        if episode % 100 == 0:
            system_metrics.append(get_system_metrics())
        
        for step in range(max_steps):
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            # Choisir la prochaine action selon la politique actuelle
            next_action = agent.choose_action(next_state)
            
            # Mettre à jour l'agent
            td_error = agent.update(state, action, reward, next_state, next_action)
            episode_td_errors.append(abs(td_error))
            
            total_reward += reward
            steps += 1
            
            if done:
                break
                
            state = next_state
            action = next_action
        
        # Métriques de l'épisode
        episode_rewards.append(total_reward)
        episode_steps.append(steps)
        episode_successes.append(1 if reward == 20 else 0)  # Taxi-v3: 20 = succès
        td_errors.extend(episode_td_errors)
        
        # Décroissance d'epsilon
        agent.decay_epsilon(eps_decay, eps_min)
        
        # Affichage de progression
        if (episode + 1) % 1000 == 0:
            recent_success_rate = np.mean(episode_successes[-1000:])
            recent_avg_steps = np.mean(episode_steps[-1000:])
            print(f"📊 Épisode {episode + 1}/{episodes} - "
                  f"Succès: {recent_success_rate*100:.1f}% - "
                  f"Pas moyen: {recent_avg_steps:.1f} - "
                  f"Epsilon: {agent.eps:.3f}")
    
    # Calcul des statistiques finales
    final_success_rate = np.mean(episode_successes)
    final_avg_steps = np.mean(episode_steps)
    final_avg_reward = np.mean(episode_rewards)
    final_td_error = np.mean(td_errors[-1000:]) if td_errors else 0
    
    print(f"✅ Entraînement terminé - "
          f"Succès: {final_success_rate*100:.1f}% - "
          f"Pas moyen: {final_avg_steps:.1f} - "
          f"Récompense moyenne: {final_avg_reward:.1f}")
    
    return {
        "episode_rewards": episode_rewards,
        "episode_steps": episode_steps,
        "episode_successes": episode_successes,
        "td_errors": td_errors,
        "system_metrics": system_metrics,
        "final_success_rate": final_success_rate,
        "final_avg_steps": final_avg_steps,
        "final_avg_reward": final_avg_reward,
        "final_td_error": final_td_error,
        "total_training_time": 0  # Sera calculé dans run_sarsa
    }

def test_agent(agent: SarsaAgent, env, episodes: int = 100, max_steps: int = 200) -> Dict[str, Any]:
    """Teste l'agent entraîné"""
    
    print(f"🧪 Test de l'agent ({episodes} épisodes)")
    
    episode_rewards = []
    episode_steps = []
    episode_successes = []
    
    for episode in range(episodes):
        state, _ = env.reset()
        total_reward = 0
        steps = 0
        
        for step in range(max_steps):
            action = agent.choose_action(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            total_reward += reward
            steps += 1
            
            if done:
                break
                
            state = next_state
        
        episode_rewards.append(total_reward)
        episode_steps.append(steps)
        episode_successes.append(1 if reward == 20 else 0)
    
    success_rate = np.mean(episode_successes)
    avg_steps = np.mean(episode_steps)
    avg_reward = np.mean(episode_rewards)
    
    print(f"✅ Test terminé - "
          f"Succès: {success_rate*100:.1f}% - "
          f"Pas moyen: {avg_steps:.1f} - "
          f"Récompense moyenne: {avg_reward:.1f}")
    
    return {
        "episode_rewards": episode_rewards,
        "episode_steps": episode_steps,
        "episode_successes": episode_successes,
        "success_rate": success_rate,
        "avg_steps": avg_steps,
        "avg_reward": avg_reward
    }

def generate_plots(training_stats: Dict[str, Any], test_stats: Dict[str, Any], 
                  brute_stats: Dict[str, Any], output_dir: Path) -> List[str]:
    """Génère les graphiques de performance"""
    
    plot_paths = []
    
    # Configuration des graphiques
    plt.style.use('seaborn-v0_8')
    fig_size = (12, 8)
    
    # 1. Récompenses par épisode
    plt.figure(figsize=fig_size)
    plt.plot(training_stats['episode_rewards'])
    plt.title('Récompenses par Épisode - Entraînement SARSA')
    plt.xlabel('Épisode')
    plt.ylabel('Récompense')
    plt.grid(True, alpha=0.3)
    plot_path = output_dir / 'rewards_per_episode.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    plot_paths.append(str(plot_path))
    
    # 2. Pas par épisode
    plt.figure(figsize=fig_size)
    plt.plot(training_stats['episode_steps'])
    plt.title('Pas par Épisode - Entraînement SARSA')
    plt.xlabel('Épisode')
    plt.ylabel('Nombre de Pas')
    plt.grid(True, alpha=0.3)
    plot_path = output_dir / 'steps_per_episode.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    plot_paths.append(str(plot_path))
    
    # 3. Taux de succès par épisode
    plt.figure(figsize=fig_size)
    window = 100
    success_rates = [np.mean(training_stats['episode_successes'][max(0, i-window):i+1]) 
                    for i in range(len(training_stats['episode_successes']))]
    plt.plot(success_rates)
    plt.title(f'Taux de Succès (moyenne glissante {window} épisodes) - Entraînement SARSA')
    plt.xlabel('Épisode')
    plt.ylabel('Taux de Succès')
    plt.grid(True, alpha=0.3)
    plot_path = output_dir / 'success_rate_per_episode.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    plot_paths.append(str(plot_path))
    
    # 4. Comparaison des performances
    plt.figure(figsize=fig_size)
    algorithms = ['SARSA', 'Brute Force']
    success_rates = [test_stats['success_rate'] * 100, brute_stats['success_rate'] * 100]
    avg_steps = [test_stats['avg_steps'], brute_stats['avg_steps']]
    
    x = np.arange(len(algorithms))
    width = 0.35
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Taux de succès
    bars1 = ax1.bar(x, success_rates, width, label='Taux de Succès (%)')
    ax1.set_xlabel('Algorithme')
    ax1.set_ylabel('Taux de Succès (%)')
    ax1.set_title('Comparaison des Taux de Succès')
    ax1.set_xticks(x)
    ax1.set_xticklabels(algorithms)
    ax1.legend()
    
    # Pas moyens
    bars2 = ax2.bar(x, avg_steps, width, label='Pas Moyens', color='orange')
    ax2.set_xlabel('Algorithme')
    ax2.set_ylabel('Pas Moyens')
    ax2.set_title('Comparaison des Pas Moyens')
    ax2.set_xticks(x)
    ax2.set_xticklabels(algorithms)
    ax2.legend()
    
    plt.tight_layout()
    plot_path = output_dir / 'performance_comparison.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    plot_paths.append(str(plot_path))
    
    return plot_paths

def save_model(agent: SarsaAgent, output_dir: Path):
    """Sauvegarde le modèle entraîné"""
    model_path = output_dir / 'sarsa_model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(agent, f)
    print(f"💾 Modèle sauvegardé: {model_path}")

def run_sarsa(params: SarsaParams, db_session=None) -> Dict[str, Any]:
    """Fonction principale pour exécuter l'algorithme SARSA"""
    
    try:
        # 1. Application des paramètres optimisés si demandé
        params = params.get_optimized_params()
        
        # 2. Génération d'un ID unique pour cette exécution
        run_id = str(uuid.uuid4())
        output_dir = Path(f"data/results/sarsa/{run_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🚕 Démarrage SARSA - Run ID: {run_id}")
        print(f"📁 Répertoire de sortie: {output_dir}")
        
        # 3. Création de l'environnement
        env = gym.make('Taxi-v3')
        
        # 4. Création et entraînement de l'agent SARSA
        sarsa_agent = SarsaAgent(
            env=env,
            alpha=params.alpha,
            gamma=params.gamma,
            eps=params.eps
        )
        
        # 5. Entraînement
        start_time = time.time()
        training_stats = train_sarsa(
            agent=sarsa_agent,
            env=env,
            episodes=params.training_runs,
            max_steps=params.maxStepsPerEpisode,
            eps_decay=params.eps_decay,
            eps_min=params.eps_min
        )
        training_time = time.time() - start_time
        training_stats["total_training_time"] = training_time
        
        # 6. Test de l'agent entraîné
        test_stats = test_agent(
            agent=sarsa_agent,
            env=env,
            episodes=params.test_episodes,
            max_steps=params.maxStepsPerEpisode
        )
        
        # 7. Comparaison avec brute force
        brute_agent = BruteForceAgent(env)
        brute_stats = test_agent(
            agent=brute_agent,
            env=env,
            episodes=params.test_episodes,
            max_steps=params.maxStepsPerEpisode
        )
        
        # 8. Génération des graphiques
        plot_paths = generate_plots(training_stats, test_stats, brute_stats, output_dir)
        
        # 9. Sauvegarde du modèle
        save_model(sarsa_agent, output_dir)
        
        # 10. Compilation des statistiques finales
        final_stats = {
            "training": training_stats,
            "test": test_stats,
            "brute_force": brute_stats,
            "system_resources": {
                "training": {
                    "avg_cpu": np.mean([m["cpu_percent"] for m in training_stats.get("system_metrics", [])]),
                    "peak_cpu": max([m["cpu_percent"] for m in training_stats.get("system_metrics", [])], default=0),
                    "avg_memory_mb": np.mean([m["memory_mb"] for m in training_stats.get("system_metrics", [])]),
                    "peak_memory_mb": max([m["memory_mb"] for m in training_stats.get("system_metrics", [])], default=0)
                }
            },
            "learning_stability": {
                "final_q_variance": float(np.var(sarsa_agent.q_table)),
                "final_epsilon": float(sarsa_agent.eps)
            },
            "improvement": {
                "steps_reduction": ((brute_stats["avg_steps"] - test_stats["avg_steps"]) / brute_stats["avg_steps"]) * 100 if brute_stats["avg_steps"] > 0 else 0,
                "efficiency_gain": brute_stats["avg_steps"] / test_stats["avg_steps"] if test_stats["avg_steps"] > 0 else 1
            }
        }
        
        # 11. Sauvegarde en base de données si disponible
        if db_session:
            try:
                from app.api.services.database_service import DatabaseService
                
                # Créer le run d'entraînement
                run_data = TrainingRunCreate(
                    algorithm="sarsa",
                    params=params.dict(),
                    training_metrics=final_stats["training"],
                    test_metrics=final_stats["test"],
                    system_metrics=final_stats["system_resources"],
                    learning_stability=final_stats["learning_stability"],
                    brute_force_metrics=final_stats["brute_force"],
                    improvement_metrics=final_stats["improvement"],
                    model_path=f"/models/sarsa/{run_id}/sarsa_model.pkl",
                    plots=[f"/assets/sarsa/{run_id}/{Path(p).name}" for p in plot_paths],
                    execution_time=final_stats["training"]["total_training_time"]
                )
                
                db_run = DatabaseService.create_training_run(db_session, run_data)
                
                # Créer l'entrée du modèle sauvegardé
                model_data = SavedModelCreate(
                    run_id=db_run.run_id,
                    model_name="sarsa_model",
                    model_path=f"/models/sarsa/{run_id}/sarsa_model.pkl",
                    model_metadata={
                        "n_states": sarsa_agent.n_states,
                        "n_actions": sarsa_agent.n_actions,
                        "q_table_stats": {
                            "mean": float(np.mean(sarsa_agent.q_table)),
                            "std": float(np.std(sarsa_agent.q_table)),
                            "variance": float(np.var(sarsa_agent.q_table)),
                            "non_zero_count": int(np.count_nonzero(sarsa_agent.q_table))
                        }
                    }
                )
                
                DatabaseService.create_saved_model(db_session, model_data)
                print(f"✅ Données sauvegardées en base avec run_id: {db_run.run_id}")
                
            except Exception as e:
                print(f"⚠️ Erreur lors de la sauvegarde en base: {e}")
        
        # 12. Sauvegarde des résultats
        results = {
            "status": "success",
            "run_id": run_id,
            "params": params.model_dump(),
            "plots": [f"/assets/sarsa/{run_id}/{Path(p).name}" for p in plot_paths],
            "model_path": f"/models/sarsa/{run_id}/sarsa_model.pkl",
            "statistics": final_stats,
            "message": f"SARSA training completed successfully. "
                      f"Agent achieves {final_stats['test']['success_rate']*100:.1f}% success rate "
                      f"with average {final_stats['test']['avg_steps']:.1f} steps per episode."
        }
        
        # Sauvegarde du rapport JSON
        with open(output_dir / 'results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        # Affichage du résumé final
        print("\n" + "="*60)
        print("🎯 SARSA TRAINING COMPLETED")
        print("="*60)
        print(f"📊 Success Rate: {final_stats['test']['success_rate']*100:.1f}%")
        print(f"🚀 Average Steps: {final_stats['test']['avg_steps']:.1f}")
        print(f"⚡ Improvement vs Brute Force: {final_stats['improvement']['steps_reduction']:.1f}%")
        print(f"⏱️  Training Time: {final_stats['training']['total_training_time']:.2f}s")
        print(f"📁 Run ID: {run_id}")
        print("="*60)
        
        env.close()
        return results
        
    except Exception as e:
        error_message = f"Error during SARSA execution: {str(e)}"
        print(f"\n❌ {error_message}")
        return {
            "status": "error",
            "message": error_message,
            "params": params.model_dump() if params else {},
            "run_id": None,
            "plots": [],
            "statistics": {}
        }
