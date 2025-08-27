from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Schémas de base
class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=255)

class UserCreate(UserBase):
    pass

class User(UserBase):
    user_id: str  # Utiliser String au lieu de UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schémas pour les runs d'entraînement
class TrainingRunBase(BaseModel):
    algorithm: str = Field(..., max_length=50)
    params: Dict[str, Any]
    status: str = Field(default="completed", max_length=50)

class TrainingRunCreate(TrainingRunBase):
    user_id: Optional[str] = None  # Utiliser String au lieu de UUID
    training_metrics: Optional[Dict[str, Any]] = None
    test_metrics: Optional[Dict[str, Any]] = None
    system_metrics: Optional[Dict[str, Any]] = None
    learning_stability: Optional[Dict[str, Any]] = None
    brute_force_metrics: Optional[Dict[str, Any]] = None
    improvement_metrics: Optional[Dict[str, Any]] = None
    model_path: Optional[str] = None
    plots: Optional[List[str]] = None
    execution_time: Optional[float] = None

class TrainingRun(TrainingRunBase):
    run_id: str  # Utiliser String au lieu de UUID
    user_id: Optional[str]  # Utiliser String au lieu de UUID
    training_metrics: Optional[Dict[str, Any]]
    test_metrics: Optional[Dict[str, Any]]
    system_metrics: Optional[Dict[str, Any]]
    learning_stability: Optional[Dict[str, Any]]
    brute_force_metrics: Optional[Dict[str, Any]]
    improvement_metrics: Optional[Dict[str, Any]]
    model_path: Optional[str]
    plots: Optional[List[str]]
    execution_time: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schémas pour les modèles sauvegardés
class SavedModelBase(BaseModel):
    model_name: str = Field(..., max_length=100)
    model_path: str = Field(..., max_length=500)
    model_size: Optional[int] = None
    model_metadata: Optional[Dict[str, Any]] = None

class SavedModelCreate(SavedModelBase):
    run_id: str  # Utiliser String au lieu de UUID

class SavedModel(SavedModelBase):
    model_id: str  # Utiliser String au lieu de UUID
    run_id: str  # Utiliser String au lieu de UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schémas pour les annotations
class RunAnnotationBase(BaseModel):
    annotation: str = Field(..., min_length=1)
    tags: Optional[List[str]] = None

class RunAnnotationCreate(RunAnnotationBase):
    run_id: str  # Utiliser String au lieu de UUID
    user_id: Optional[str] = None  # Utiliser String au lieu de UUID

class RunAnnotation(RunAnnotationBase):
    annotation_id: int  # Utiliser int car c'est un Integer dans le modèle
    run_id: str  # Utiliser String au lieu de UUID
    user_id: Optional[str]  # Utiliser String au lieu de UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schémas pour les requêtes et réponses
class TrainingRunSummary(BaseModel):
    """Résumé d'un run pour les listes"""
    run_id: str  # Utiliser String au lieu de UUID
    algorithm: str
    success_rate: Optional[float] = None
    avg_steps: Optional[float] = None
    execution_time: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class TrainingRunWithDetails(TrainingRun):
    """Run complet avec toutes les métriques"""
    saved_models: List[SavedModel] = []
    annotations: List[RunAnnotation] = []
    
    class Config:
        from_attributes = True

class StatisticsResponse(BaseModel):
    """Statistiques globales"""
    total_runs: int
    algorithms: List[str]
    best_success_rate: float
    best_avg_steps: float
    total_execution_time: float

class ComparisonRequest(BaseModel):
    """Requête pour comparer des runs"""
    run_ids: List[str] = Field(..., min_items=2, max_items=10)  # Utiliser String au lieu de UUID

class ComparisonResponse(BaseModel):
    """Réponse de comparaison"""
    runs: List[TrainingRun]
    comparison_metrics: Dict[str, Any]
