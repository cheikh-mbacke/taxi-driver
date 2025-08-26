import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os
import uuid
import json
import pickle
import psutil
from pathlib import Path
from typing import Dict, List, Tuple, Any

from app.schemas.sarsa import SarsaParams
from app.services.base_agent import BaseAgent, BruteForceAgent

def get_system_metrics():
    """Récupère les métriques système en temps réel (CPU + RAM seulement)"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        return {
            'cpu_percent': cpu_percent,
            'memory_mb': memory,
            'gpu_util': 0,  # GPU désactivé pour éviter le problème
            'gpu_memory': 0
        }
    except:
        # Fallback si erreur système
        return {
            'cpu_percent': 0,
            'memory_mb': 0,
            'gpu_util': 0,
            'gpu_memory': 0
        }

class SarsaAgent(BaseAgent):
    """Agent SARSA pour l'environnement Taxi-v3 avec métriques étendues"""
    
    def __init__(self, env: gym.Env, params: SarsaParams):
        super().__init__(env)
        self.params = params
        
        # Initialisation de la Q-table
        self.q_table = np.zeros((self.n_states, self.n_actions))
        
        # Paramètres
        self.alpha = params.alpha
        self.gamma = params.gamma
        self.epsilon = params.eps
        self.epsilon_decay = params.eps_decay
        self.epsilon_min = params.eps_min
        
        # Historique des erreurs TD pour métriques
        self.td_errors_history = []
        
    def get_action(self, state: int) -> int:
        """Politique epsilon-greedy"""
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()
        return np.argmax(self.q_table[state])
    
    def update(self, state: int, action: int, reward: float, 
               next_state: int, next_action: int = None) -> float:
        """Mise à jour SARSA de la Q-table avec retour de l'erreur TD"""
        if next_action is None:
            next_action = self.get_action(next_state)
            
        td_error = reward + self.gamma * self.q_table[next_state, next_action] - self.q_table[state, action]
        self.q_table[state, action] += self.alpha * td_error
        
        # Stocker l'erreur TD absolue pour les métriques
        abs_td_error = abs(td_error)
        self.td_errors_history.append(abs_td_error)
        
        return abs_td_error
    
    def decay_epsilon(self) -> None:
        """Décroissance de l'epsilon"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

def train_sarsa(agent: SarsaAgent, params: SarsaParams) -> Dict[str, List]:
    """Entraînement de l'agent SARSA avec métriques système étendues"""
    metrics = {
        # Métriques originales
        'episode': [],
        'rewards': [],
        'steps': [],
        'cumulative_time': [],
        'epsilon': [],
        
        # Nouvelles métriques système (GPU désactivé)
        'cpu_usage': [],
        'memory_usage': [],
        'gpu_usage': [],
        'gpu_memory': [],
        'avg_td_error': [],
        'q_table_variance': [],
        'q_table_mean': [],
        'q_table_std': []
    }
    
    start_time = time.time()
    
    for episode in range(params.training_runs):
        state, _ = agent.env.reset()
        action = agent.get_action(state)
        total_reward = 0
        steps = 0
        episode_td_errors = []
        
        # Métriques système au début de l'épisode
        sys_metrics = get_system_metrics()
        
        for _ in range(params.maxStepsPerEpisode):
            next_state, reward, terminated, truncated, _ = agent.env.step(action)
            done = terminated or truncated
            next_action = agent.get_action(next_state)
            
            # Mise à jour SARSA avec récupération de l'erreur TD
            td_error = agent.update(state, action, reward, next_state, next_action)
            episode_td_errors.append(td_error)
            
            total_reward += reward
            steps += 1
            
            state = next_state
            action = next_action
            
            if done:
                break
        
        # Décroissance epsilon
        agent.decay_epsilon()
        
        # Calcul des statistiques de la Q-table
        q_non_zero = agent.q_table[agent.q_table != 0]
        q_variance = np.var(q_non_zero) if len(q_non_zero) > 0 else 0
        q_mean = np.mean(q_non_zero) if len(q_non_zero) > 0 else 0
        q_std = np.std(q_non_zero) if len(q_non_zero) > 0 else 0
        
        # Enregistrement des métriques
        metrics['episode'].append(episode)
        metrics['rewards'].append(total_reward)
        metrics['steps'].append(steps)
        metrics['cumulative_time'].append(time.time() - start_time)
        metrics['epsilon'].append(agent.epsilon)
        
        # Nouvelles métriques
        metrics['cpu_usage'].append(sys_metrics['cpu_percent'])
        metrics['memory_usage'].append(sys_metrics['memory_mb'])
        metrics['gpu_usage'].append(0)  # GPU désactivé
        metrics['gpu_memory'].append(0)  # GPU désactivé
        metrics['avg_td_error'].append(np.mean(episode_td_errors) if episode_td_errors else 0)
        metrics['q_table_variance'].append(q_variance)
        metrics['q_table_mean'].append(q_mean)
        metrics['q_table_std'].append(q_std)
        
        # Affichage progression avec nouvelles métriques
        if episode % 100 == 0:
            avg_reward = np.mean(metrics['rewards'][-100:]) if len(metrics['rewards']) >= 100 else np.mean(metrics['rewards'])
            avg_td_error = np.mean(metrics['avg_td_error'][-100:]) if len(metrics['avg_td_error']) >= 100 else np.mean(metrics['avg_td_error'])
            print(f"Episode {episode}/{params.training_runs} - Avg Reward: {avg_reward:.2f} - "
                  f"Epsilon: {agent.epsilon:.3f} - TD Error: {avg_td_error:.4f} - "
                  f"CPU: {sys_metrics['cpu_percent']:.1f}% - RAM: {sys_metrics['memory_mb']:.0f}MB - "
                  f"Q-table Var: {q_variance:.4f}")
    
    return metrics

def test_agent(agent: BaseAgent, env: gym.Env, n_episodes: int, max_steps: int) -> Dict[str, List]:
    """Test d'un agent (SARSA ou BruteForce) avec métriques système"""
    metrics = {
        'rewards': [],
        'steps': [],
        'success_rate': 0,
        'cpu_usage': [],
        'memory_usage': [],
        'gpu_usage': [],
        'gpu_memory': []
    }
    
    successful_episodes = 0
    
    for episode in range(n_episodes):
        state, _ = env.reset()
        total_reward = 0
        steps = 0
        
        # Métriques système pour le test
        sys_metrics = get_system_metrics()
        
        for _ in range(max_steps):
            if hasattr(agent, 'epsilon'):
                # Pour SARSA, on désactive l'exploration pendant le test
                old_epsilon = agent.epsilon
                agent.epsilon = 0
                action = agent.get_action(state)
                agent.epsilon = old_epsilon
            else:
                # Pour BruteForce
                action = agent.get_action(state)
            
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            total_reward += reward
            steps += 1
            state = next_state
            
            if done:
                if reward == 20:  # Succès dans Taxi-v3
                    successful_episodes += 1
                break
        
        metrics['rewards'].append(total_reward)
        metrics['steps'].append(steps)
        metrics['cpu_usage'].append(sys_metrics['cpu_percent'])
        metrics['memory_usage'].append(sys_metrics['memory_mb'])
        metrics['gpu_usage'].append(0)  # GPU désactivé
        metrics['gpu_memory'].append(0)  # GPU désactivé
    
    metrics['success_rate'] = successful_episodes / n_episodes
    return metrics

def generate_plots(train_metrics: Dict, test_metrics: Dict, brute_metrics: Dict, 
                   output_dir: Path) -> List[str]:
    """Génération des graphiques de métriques étendus"""
    plt.style.use('seaborn-v0_8-darkgrid')
    plots = []
    
    # 1. Reward par épisode (graphique original)
    plt.figure(figsize=(12, 6))
    
    window = 100
    rewards_smooth = np.convolve(train_metrics['rewards'], 
                                np.ones(window)/window, mode='valid')
    episodes_smooth = train_metrics['episode'][window-1:]
    
    plt.plot(train_metrics['episode'], train_metrics['rewards'], 
             alpha=0.3, color='blue', label='Rewards par épisode')
    plt.plot(episodes_smooth, rewards_smooth, 
             color='darkblue', linewidth=2, label=f'Moyenne mobile ({window} eps)')
    
    plt.xlabel('Épisode')
    plt.ylabel('Reward')
    plt.title('SARSA - Reward par épisode pendant l\'entraînement')
    plt.legend()
    plt.tight_layout()
    
    plot_path = output_dir / 'reward_per_episode.png'
    plt.savefig(plot_path, dpi=150)
    plt.close()
    plots.append(str(plot_path))
    
    # 2. Nombre de pas par épisode (graphique original)
    plt.figure(figsize=(12, 6))
    
    steps_smooth = np.convolve(train_metrics['steps'], 
                              np.ones(window)/window, mode='valid')
    
    plt.plot(train_metrics['episode'], train_metrics['steps'], 
             alpha=0.3, color='green', label='Pas par épisode')
    plt.plot(episodes_smooth, steps_smooth, 
             color='darkgreen', linewidth=2, label=f'Moyenne mobile ({window} eps)')
    
    plt.xlabel('Épisode')
    plt.ylabel('Nombre de pas')
    plt.title('SARSA - Nombre de pas par épisode pendant l\'entraînement')
    plt.legend()
    plt.tight_layout()
    
    plot_path = output_dir / 'steps_per_episode.png'
    plt.savefig(plot_path, dpi=150)
    plt.close()
    plots.append(str(plot_path))
    
    # 3. Temps cumulé (graphique original)
    plt.figure(figsize=(12, 6))
    plt.plot(train_metrics['episode'], train_metrics['cumulative_time'], 
             color='red', linewidth=2)
    plt.xlabel('Épisode')
    plt.ylabel('Temps cumulé (secondes)')
    plt.title('SARSA - Temps cumulé d\'entraînement')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plot_path = output_dir / 'cumulative_time.png'
    plt.savefig(plot_path, dpi=150)
    plt.close()
    plots.append(str(plot_path))
    
    # 4. Graphique de comparaison original
    plt.figure(figsize=(14, 8))
    
    # Calcul des moyennes par blocs de 100
    block_size = 100
    n_blocks = len(train_metrics['rewards']) // block_size
    
    avg_rewards_blocks = []
    avg_steps_blocks = []
    block_episodes = []
    
    for i in range(n_blocks):
        start_idx = i * block_size
        end_idx = (i + 1) * block_size
        avg_rewards_blocks.append(np.mean(train_metrics['rewards'][start_idx:end_idx]))
        avg_steps_blocks.append(np.mean(train_metrics['steps'][start_idx:end_idx]))
        block_episodes.append((i + 1) * block_size)
    
    # Subplot 1: Rewards moyens
    plt.subplot(2, 2, 1)
    plt.plot(block_episodes, avg_rewards_blocks, 'o-', color='blue', markersize=6)
    plt.xlabel('Épisode')
    plt.ylabel('Reward moyen / 100 eps')
    plt.title('Score moyen par 100 épisodes')
    plt.grid(True, alpha=0.3)
    
    # Subplot 2: Steps moyens
    plt.subplot(2, 2, 2)
    plt.plot(block_episodes, avg_steps_blocks, 'o-', color='green', markersize=6)
    plt.xlabel('Épisode')
    plt.ylabel('Pas moyens / 100 eps')
    plt.title('Pas moyens par 100 épisodes')
    plt.grid(True, alpha=0.3)
    
    # Subplot 3: Comparaison SARSA vs Brute Force
    plt.subplot(2, 2, 3)
    labels = ['SARSA', 'Brute Force']
    avg_steps = [np.mean(test_metrics['steps']), np.mean(brute_metrics['steps'])]
    colors = ['blue', 'red']
    
    bars = plt.bar(labels, avg_steps, color=colors, alpha=0.7)
    plt.ylabel('Nombre moyen de pas')
    plt.title('Comparaison: Nombre de pas moyen (Test)')
    
    for bar, value in zip(bars, avg_steps):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # Subplot 4: Taux de succès
    plt.subplot(2, 2, 4)
    success_rates = [test_metrics['success_rate'] * 100, brute_metrics['success_rate'] * 100]
    bars = plt.bar(labels, success_rates, color=colors, alpha=0.7)
    plt.ylabel('Taux de succès (%)')
    plt.title('Comparaison: Taux de succès (Test)')
    plt.ylim(0, 105)
    
    for bar, value in zip(bars, success_rates):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plot_path = output_dir / 'performance_comparison.png'
    plt.savefig(plot_path, dpi=150)
    plt.close()
    plots.append(str(plot_path))
    
    # 5. Métriques système étendues (sans GPU)
    plt.figure(figsize=(18, 10))
    
    # CPU Usage
    plt.subplot(2, 3, 1)
    plt.plot(train_metrics['episode'], train_metrics['cpu_usage'], color='red', linewidth=2)
    plt.xlabel('Épisode')
    plt.ylabel('CPU (%)')
    plt.title('Utilisation CPU pendant l\'entraînement')
    plt.grid(True, alpha=0.3)
    
    # Memory Usage
    plt.subplot(2, 3, 2)
    plt.plot(train_metrics['episode'], train_metrics['memory_usage'], color='blue', linewidth=2)
    plt.xlabel('Épisode')
    plt.ylabel('RAM (MB)')
    plt.title('Utilisation RAM pendant l\'entraînement')
    plt.grid(True, alpha=0.3)
    
    # TD Error Evolution
    plt.subplot(2, 3, 3)
    if len(train_metrics['avg_td_error']) >= window:
        td_smooth = np.convolve(train_metrics['avg_td_error'], 
                               np.ones(window)/window, mode='valid')
        episodes_smooth = train_metrics['episode'][window-1:]
        plt.plot(episodes_smooth, td_smooth, color='purple', linewidth=2, label=f'Moyenne mobile ({window})')
    plt.plot(train_metrics['episode'], train_metrics['avg_td_error'], 
             alpha=0.3, color='purple', label='TD Error brut')
    plt.xlabel('Épisode')
    plt.ylabel('Erreur TD moyenne')
    plt.title('Évolution de l\'erreur TD (apprentissage)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Q-table Variance (stabilité)
    plt.subplot(2, 3, 4)
    plt.plot(train_metrics['episode'], train_metrics['q_table_variance'], 
             color='orange', linewidth=2)
    plt.xlabel('Épisode')
    plt.ylabel('Variance Q-table')
    plt.title('Stabilité de la Q-table')
    plt.grid(True, alpha=0.3)
    
    # Q-table Statistics
    plt.subplot(2, 3, 5)
    plt.plot(train_metrics['episode'], train_metrics['q_table_mean'], 
             color='cyan', linewidth=2, label='Moyenne')
    plt.plot(train_metrics['episode'], train_metrics['q_table_std'], 
             color='magenta', linewidth=2, label='Écart-type')
    plt.xlabel('Épisode')
    plt.ylabel('Valeur')
    plt.title('Statistiques Q-table')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Resource Usage Summary (CPU + RAM seulement)
    plt.subplot(2, 3, 6)
    final_cpu = np.mean(train_metrics['cpu_usage'][-100:]) if len(train_metrics['cpu_usage']) >= 100 else np.mean(train_metrics['cpu_usage'])
    final_ram = np.mean(train_metrics['memory_usage'][-100:]) if len(train_metrics['memory_usage']) >= 100 else np.mean(train_metrics['memory_usage'])
    
    resources = ['CPU (%)', 'RAM (MB/100)']
    values = [final_cpu, final_ram/100]
    colors = ['red', 'blue']
    
    bars = plt.bar(resources, values, color=colors, alpha=0.7)
    plt.ylabel('Utilisation moyenne (derniers 100 épisodes)')
    plt.title('Résumé utilisation ressources (CPU + RAM)')
    
    for bar, value, original in zip(bars, values, [final_cpu, final_ram]):
        display_value = original if bar.get_x() != 1 else original
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                f'{display_value:.1f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plot_path = output_dir / 'system_and_learning_metrics.png'
    plt.savefig(plot_path, dpi=150)
    plt.close()
    plots.append(str(plot_path))
    
    return plots

def save_model(agent: SarsaAgent, output_dir: Path) -> str:
    """Sauvegarde du modèle entraîné avec statistiques étendues"""
    model_path = output_dir / 'sarsa_model.pkl'
    model_data = {
        'q_table': agent.q_table,
        'params': agent.params.dict(),
        'n_states': agent.n_states,
        'n_actions': agent.n_actions,
        'td_errors_history': agent.td_errors_history[-1000:],  # Garder les 1000 dernières erreurs
        'q_table_stats': {
            'mean': np.mean(agent.q_table),
            'std': np.std(agent.q_table),
            'variance': np.var(agent.q_table),
            'non_zero_count': np.count_nonzero(agent.q_table),
            'max_value': np.max(agent.q_table),
            'min_value': np.min(agent.q_table)
        }
    }
    
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    return str(model_path)

def run_sarsa(params: SarsaParams) -> Dict[str, Any]:
    """Fonction principale pour exécuter SARSA avec métriques étendues"""
    try:
        # Appliquer les paramètres optimisés si nécessaire
        params = params.get_optimized_params()
        
        # Création de l'environnement
        env = gym.make('Taxi-v3')
        
        # Génération du GUID pour ce run
        run_id = str(uuid.uuid4())
        
        # Création des dossiers de sortie
        output_dir = Path(f"assets/images/sarsa/{run_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        model_dir = Path(f"models/sarsa/{run_id}")
        model_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Starting SARSA training with extended metrics (CPU+RAM only): {params.dict()}")
        
        # 1. Entraînement SARSA
        sarsa_agent = SarsaAgent(env, params)
        train_metrics = train_sarsa(sarsa_agent, params)
        
        # 2. Test SARSA
        print("\nTesting SARSA agent...")
        test_metrics = test_agent(sarsa_agent, env, params.test_episodes, params.maxStepsPerEpisode)
        
        # 3. Brute Force pour comparaison
        print("\nTesting Brute Force agent for comparison...")
        brute_agent = BruteForceAgent(env)
        brute_metrics = test_agent(brute_agent, env, params.test_episodes, params.maxStepsPerEpisode)
        
        # 4. Génération des graphiques
        print("\nGenerating extended plots...")
        plot_paths = generate_plots(train_metrics, test_metrics, brute_metrics, output_dir)
        
        # 5. Sauvegarde du modèle
        model_path = save_model(sarsa_agent, model_dir)
        
        # 6. Calcul des statistiques finales étendues
        final_stats = {
            "training": {
                "final_reward_avg": np.mean(train_metrics['rewards'][-100:]),
                "final_steps_avg": np.mean(train_metrics['steps'][-100:]),
                "final_td_error": np.mean(train_metrics['avg_td_error'][-100:]),
                "final_q_table_variance": train_metrics['q_table_variance'][-1],
                "total_training_time": train_metrics['cumulative_time'][-1],
                "episodes": params.training_runs
            },
            "test": {
                "avg_reward": np.mean(test_metrics['rewards']),
                "avg_steps": np.mean(test_metrics['steps']),
                "success_rate": test_metrics['success_rate'],
                "episodes": params.test_episodes
            },
            "system_resources": {
                "training": {
                    "avg_cpu": np.mean(train_metrics['cpu_usage']),
                    "avg_memory_mb": np.mean(train_metrics['memory_usage']),
                    "avg_gpu": 0,  # GPU désactivé
                    "peak_memory_mb": np.max(train_metrics['memory_usage']),
                    "peak_cpu": np.max(train_metrics['cpu_usage'])
                },
                "test_sarsa": {
                    "avg_cpu": np.mean(test_metrics['cpu_usage']) if test_metrics['cpu_usage'] else 0,
                    "avg_memory_mb": np.mean(test_metrics['memory_usage']) if test_metrics['memory_usage'] else 0
                },
                "test_brute": {
                    "avg_cpu": np.mean(brute_metrics['cpu_usage']) if brute_metrics['cpu_usage'] else 0,
                    "avg_memory_mb": np.mean(brute_metrics['memory_usage']) if brute_metrics['memory_usage'] else 0
                }
            },
            "learning_stability": {
                "final_q_variance": train_metrics['q_table_variance'][-1],
                "q_table_mean": train_metrics['q_table_mean'][-1],
                "q_table_std": train_metrics['q_table_std'][-1],
                "td_error_trend": "decreasing" if len(train_metrics['avg_td_error']) > 100 and 
                                 train_metrics['avg_td_error'][-1] < train_metrics['avg_td_error'][100] else "stable",
                "convergence_episode": None
            },
            "brute_force": {
                "avg_reward": np.mean(brute_metrics['rewards']),
                "avg_steps": np.mean(brute_metrics['steps']),
                "success_rate": brute_metrics['success_rate']
            },
            "improvement": {
                "steps_reduction": (np.mean(brute_metrics['steps']) - np.mean(test_metrics['steps'])) / np.mean(brute_metrics['steps']) * 100,
                "success_rate_increase": (test_metrics['success_rate'] - brute_metrics['success_rate']) * 100,
                "efficiency_gain": np.mean(brute_metrics['steps']) / np.mean(test_metrics['steps']) if np.mean(test_metrics['steps']) > 0 else 1
            }
        }
        
        # 7. Sauvegarde des résultats
        results = {
            "status": "success",
            "run_id": run_id,
            "params": params.dict(),
            "plots": [f"/assets/images/sarsa/{run_id}/{Path(p).name}" for p in plot_paths],
            "model_path": f"/models/sarsa/{run_id}/sarsa_model.pkl",
            "statistics": final_stats,
            "message": f"SARSA training with extended metrics completed successfully. "
                      f"Agent achieves {final_stats['test']['success_rate']*100:.1f}% success rate "
                      f"with average {final_stats['test']['avg_steps']:.1f} steps per episode. "
                      f"Avg CPU: {final_stats['system_resources']['training']['avg_cpu']:.1f}%, "
                      f"Peak RAM: {final_stats['system_resources']['training']['peak_memory_mb']:.0f}MB, "
                      f"Final TD Error: {final_stats['training']['final_td_error']:.4f}"
        }
        
        # Sauvegarde du rapport JSON
        with open(output_dir / 'results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        # Affichage du résumé final
        print("\n" + "="*60)
        print("🎯 SARSA TRAINING COMPLETED WITH EXTENDED METRICS")
        print("="*60)
        print(f"📊 Success Rate: {final_stats['test']['success_rate']*100:.1f}%")
        print(f"🚀 Average Steps: {final_stats['test']['avg_steps']:.1f}")
        print(f"⚡ Improvement vs Brute Force: {final_stats['improvement']['steps_reduction']:.1f}%")
        print(f"🧠 Final TD Error: {final_stats['training']['final_td_error']:.4f}")
        print(f"💻 Peak CPU: {final_stats['system_resources']['training']['peak_cpu']:.1f}%")
        print(f"🔧 Peak RAM: {final_stats['system_resources']['training']['peak_memory_mb']:.0f}MB")
        print(f"📈 Q-table Variance: {final_stats['learning_stability']['final_q_variance']:.6f}")
        print(f"⏱️  Training Time: {final_stats['training']['total_training_time']:.2f}s")
        print(f"📁 Run ID: {run_id}")
        print("⚠️  Note: GPU monitoring disabled (compatibility)")
        print("="*60)
        
        env.close()
        return results
        
    except Exception as e:
        error_message = f"Error during extended SARSA execution: {str(e)}"
        print(f"\n❌ {error_message}")
        return {
            "status": "error",
            "message": error_message,
            "params": params.dict() if params else {},
            "run_id": None,
            "plots": [],
            "statistics": {}
        }
