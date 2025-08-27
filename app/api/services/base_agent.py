from abc import ABC, abstractmethod
import numpy as np
import gymnasium as gym
from typing import Dict, List, Tuple, Any

class BaseAgent(ABC):
    """Classe de base pour tous les agents de reinforcement learning"""
    
    def __init__(self, env: gym.Env, **kwargs):
        """
        Initialisation de l'agent de base
        
        Args:
            env: Environnement Gymnasium
            **kwargs: Paramètres spécifiques à l'agent
        """
        self.env = env
        self.n_states = env.observation_space.n
        self.n_actions = env.action_space.n
        
    @abstractmethod
    def get_action(self, state: int) -> int:
        """
        Sélectionne une action pour un état donné
        
        Args:
            state: État actuel
            
        Returns:
            Action sélectionnée
        """
        pass
    
    @abstractmethod
    def update(self, state: int, action: int, reward: float, 
               next_state: int, **kwargs) -> float:
        """
        Met à jour l'agent avec l'expérience (state, action, reward, next_state)
        
        Args:
            state: État actuel
            action: Action effectuée
            reward: Récompense reçue
            next_state: État suivant
            **kwargs: Paramètres supplémentaires spécifiques à l'algorithme
            
        Returns:
            Erreur TD ou métrique d'apprentissage
        """
        pass
    
    @abstractmethod
    def decay_epsilon(self) -> None:
        """Décroissance de l'epsilon pour l'exploration"""
        pass
    
    def reset_episode(self) -> None:
        """Réinitialise l'agent pour un nouvel épisode"""
        pass

class BruteForceAgent(BaseAgent):
    """Agent de référence utilisant des actions aléatoires"""
    
    def __init__(self, env: gym.Env):
        super().__init__(env)
    
    def get_action(self, state: int) -> int:
        """Action aléatoire"""
        return self.env.action_space.sample()
    
    def choose_action(self, state: int) -> int:
        """Alias pour get_action pour compatibilité"""
        return self.get_action(state)
    
    def update(self, state: int, action: int, reward: float, 
               next_state: int, **kwargs) -> float:
        """Pas de mise à jour pour l'agent brute force"""
        return 0.0
    
    def decay_epsilon(self) -> None:
        """Pas de décroissance epsilon pour l'agent brute force"""
        pass
