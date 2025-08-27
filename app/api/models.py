from sqlalchemy import Column, Integer, String, DateTime, Text, ARRAY, JSON, ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.api.database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String(36), primary_key=True, index=True)  # Utiliser String pour UUID
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    training_runs = relationship("TrainingRun", back_populates="user")
    annotations = relationship("RunAnnotation", back_populates="user")

class TrainingRun(Base):
    __tablename__ = "training_runs"
    
    run_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)  # Utiliser String pour UUID
    algorithm = Column(String(50), nullable=False, default="sarsa")
    params = Column(JSONB, nullable=False)  # Paramètres d'entraînement
    training_metrics = Column(JSONB)  # Métriques d'entraînement
    test_metrics = Column(JSONB)  # Métriques de test
    system_metrics = Column(JSONB)  # Métriques système (CPU, RAM)
    learning_stability = Column(JSONB)  # Stabilité de l'apprentissage
    brute_force_metrics = Column(JSONB)  # Comparaison avec brute force
    improvement_metrics = Column(JSONB)  # Métriques d'amélioration
    plots = Column(JSONB)  # Chemins des graphiques générés
    model_path = Column(String(255))  # Chemin du modèle sauvegardé
    execution_time = Column(Float)  # Temps d'exécution en secondes
    status = Column(String(20), default="completed")  # completed, failed, running
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="training_runs")
    saved_models = relationship("SavedModel", back_populates="training_run")
    annotations = relationship("RunAnnotation", back_populates="training_run")

class SavedModel(Base):
    __tablename__ = "saved_models"
    
    model_id = Column(String(36), primary_key=True, index=True)
    run_id = Column(String(36), ForeignKey("training_runs.run_id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    model_path = Column(String(255), nullable=False)
    model_size = Column(Integer)  # Taille en bytes
    model_metadata = Column(JSONB)  # Métadonnées du modèle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    training_run = relationship("TrainingRun", back_populates="saved_models")

class RunAnnotation(Base):
    __tablename__ = "run_annotations"
    
    annotation_id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(36), ForeignKey("training_runs.run_id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)  # Utiliser String pour UUID
    annotation = Column(Text, nullable=False)
    tags = Column(ARRAY(String))  # Tags pour catégoriser
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    training_run = relationship("TrainingRun", back_populates="annotations")
    user = relationship("User", back_populates="annotations")
