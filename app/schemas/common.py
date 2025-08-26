from pydantic import BaseModel, Field
from typing import Optional

class CommonParams(BaseModel):
    """Paramètres communs à tous les algorithmes de reinforcement learning"""
    
    # Paramètres d'apprentissage
    alpha: Optional[float] = Field(
        default=0.1, 
        ge=0.001, 
        le=1.0, 
        description="Taux d'apprentissage"
    )
    gamma: Optional[float] = Field(
        default=0.99, 
        ge=0.1, 
        le=1.0, 
        description="Facteur d'actualisation"
    )
    eps: Optional[float] = Field(
        default=1.0, 
        ge=0.0, 
        le=1.0, 
        description="Epsilon initial pour l'exploration"
    )
    eps_decay: Optional[float] = Field(
        default=0.995, 
        ge=0.9, 
        le=1.0, 
        description="Décroissance d'epsilon"
    )
    eps_min: Optional[float] = Field(
        default=0.01, 
        ge=0.0, 
        le=0.5, 
        description="Epsilon minimum"
    )
    training_runs: Optional[int] = Field(
        default=1000, 
        ge=100, 
        le=10000, 
        description="Nombre d'épisodes d'entraînement"
    )
    maxStepsPerEpisode: Optional[int] = Field(
        default=200, 
        ge=50, 
        le=1000, 
        description="Nombre maximum de pas par épisode"
    )
