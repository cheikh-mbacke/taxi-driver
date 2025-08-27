from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from typing import List, Optional, Dict, Any
import json

from app.api.models import TrainingRun, SavedModel, RunAnnotation, User
from app.api.schemas.database import (
    TrainingRunCreate, SavedModelCreate, RunAnnotationCreate,
    TrainingRunSummary, StatisticsResponse, ComparisonRequest, ComparisonResponse
)

class DatabaseService:
    """Service pour gérer les opérations de base de données"""
    
    @staticmethod
    def create_training_run(db: Session, run_data: TrainingRunCreate) -> TrainingRun:
        """Crée un nouveau run d'entraînement"""
        # S'assurer que le run_id est défini
        run_dict = run_data.dict()
        if 'run_id' not in run_dict or not run_dict['run_id']:
            import uuid
            run_dict['run_id'] = str(uuid.uuid4())
        
        # Définir un user_id par défaut si non fourni
        if 'user_id' not in run_dict or run_dict['user_id'] is None:
            run_dict['user_id'] = "00000000-0000-0000-0000-000000000001"  # UUID de l'utilisateur par défaut
        
        db_run = TrainingRun(**run_dict)
        db.add(db_run)
        db.commit()
        db.refresh(db_run)
        return db_run
    
    @staticmethod
    def get_training_run(db: Session, run_id: str) -> Optional[TrainingRun]:
        """Récupère un run d'entraînement par son ID"""
        try:
            run = db.query(TrainingRun).filter(TrainingRun.run_id == run_id).first()
            if not run:
                return None
            
            # Convertir l'objet de base de données en dictionnaire avec les bonnes conversions
            run_dict = {
                'run_id': str(run.run_id),  # Convertir UUID en string
                'user_id': str(run.user_id) if run.user_id else None,  # Convertir UUID en string
                'algorithm': run.algorithm,
                'params': run.params,
                'training_metrics': run.training_metrics,
                'test_metrics': run.test_metrics,
                'system_metrics': run.system_metrics,
                'learning_stability': run.learning_stability,
                'brute_force_metrics': run.brute_force_metrics,
                'improvement_metrics': run.improvement_metrics,
                'model_path': run.model_path,
                'plots': run.plots,
                'execution_time': run.execution_time,
                'status': run.status,
                'created_at': run.created_at,
                'updated_at': run.updated_at or run.created_at,  # Utiliser created_at si updated_at est None
            }
            
            return TrainingRun(**run_dict)
        except Exception as e:
            print(f"Erreur lors de la récupération du run {run_id}: {e}")
            return None
    
    @staticmethod
    def get_training_runs(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        algorithm: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[TrainingRun]:
        """Récupère une liste de runs d'entraînement avec filtres"""
        query = db.query(TrainingRun)
        
        if algorithm:
            query = query.filter(TrainingRun.algorithm == algorithm)
        if user_id:
            query = query.filter(TrainingRun.user_id == user_id)
            
        return query.order_by(desc(TrainingRun.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_training_run_summaries(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        algorithm: Optional[str] = None
    ) -> List[TrainingRunSummary]:
        """Récupère des résumés de runs pour les listes"""
        try:
            # Requête simplifiée sans extraction JSON complexe
            query = db.query(
                TrainingRun.run_id,
                TrainingRun.algorithm,
                TrainingRun.execution_time,
                TrainingRun.created_at,
                TrainingRun.test_metrics
            )
            
            if algorithm:
                query = query.filter(TrainingRun.algorithm == algorithm)
                
            results = query.order_by(desc(TrainingRun.created_at)).offset(skip).limit(limit).all()
            
            summaries = []
            for result in results:
                # Extraction des métriques JSONB (retourne directement des objets Python)
                test_metrics = result.test_metrics or {}
                
                # JSONB retourne directement des objets Python, pas des chaînes
                success_rate = test_metrics.get('success_rate')
                avg_steps = test_metrics.get('avg_steps')
                
                summaries.append(TrainingRunSummary(
                    run_id=str(result.run_id),  # Convertir UUID en string
                    algorithm=result.algorithm,
                    success_rate=float(success_rate) if success_rate is not None else None,
                    avg_steps=float(avg_steps) if avg_steps is not None else None,
                    execution_time=result.execution_time,
                    created_at=result.created_at
                ))
            
            return summaries
        except Exception as e:
            # En cas d'erreur, retourner une liste vide
            print(f"Erreur lors de la récupération des runs: {e}")
            return []
    
    @staticmethod
    def get_best_runs(
        db: Session,
        limit: int = 10
    ) -> List[TrainingRunSummary]:
        """Récupère les meilleurs runs basés sur le taux de succès"""
        try:
            # Récupérer tous les runs complétés
            completed_runs = db.query(TrainingRun).filter(TrainingRun.status == 'completed').all()
            
            # Trier par taux de succès
            sorted_runs = []
            for run in completed_runs:
                if run.test_metrics:
                    # JSONB retourne directement des objets Python
                    success_rate = run.test_metrics.get('success_rate', 0)
                    avg_steps = run.test_metrics.get('avg_steps', 0)
                    
                    sorted_runs.append({
                        'run': run,
                        'success_rate': success_rate,
                        'avg_steps': avg_steps
                    })
            
            # Trier par taux de succès décroissant
            sorted_runs.sort(key=lambda x: x['success_rate'], reverse=True)
            
            # Prendre les meilleurs
            best_runs = sorted_runs[:limit]
            
            return [
                TrainingRunSummary(
                    run_id=str(item['run'].run_id),  # Convertir UUID en string
                    algorithm=item['run'].algorithm,
                    success_rate=float(item['success_rate']) if item['success_rate'] is not None else None,
                    avg_steps=float(item['avg_steps']) if item['avg_steps'] is not None else None,
                    execution_time=item['run'].execution_time,
                    created_at=item['run'].created_at
                )
                for item in best_runs
            ]
        except Exception as e:
            print(f"Erreur lors de la récupération des meilleurs runs: {e}")
            return []
    
    @staticmethod
    def get_statistics(db: Session) -> StatisticsResponse:
        """Récupère les statistiques globales"""
        try:
            # Statistiques de base
            total_runs = db.query(func.count(TrainingRun.run_id)).scalar() or 0
            
            # Algorithmes uniques
            algorithms = [row[0] for row in db.query(TrainingRun.algorithm.distinct()).all()]
            
            # Récupérer tous les runs complétés pour calculer les statistiques
            completed_runs = db.query(TrainingRun).filter(TrainingRun.status == 'completed').all()
            
            # Calculer les meilleures performances manuellement
            best_success_rate = 0.0
            best_avg_steps = float('inf')
            
            for run in completed_runs:
                if run.test_metrics:
                    # JSONB retourne directement des objets Python
                    success_rate = run.test_metrics.get('success_rate')
                    avg_steps = run.test_metrics.get('avg_steps')
                    
                    if success_rate is not None and success_rate > best_success_rate:
                        best_success_rate = success_rate
                    
                    if avg_steps is not None and avg_steps < best_avg_steps:
                        best_avg_steps = avg_steps
            
            # Si aucun run complété, utiliser 0.0
            if best_avg_steps == float('inf'):
                best_avg_steps = 0.0
            
            # Temps total d'exécution
            total_execution_time = db.query(func.sum(TrainingRun.execution_time)).scalar() or 0.0
            
            return StatisticsResponse(
                total_runs=total_runs,
                algorithms=algorithms,
                best_success_rate=float(best_success_rate),
                best_avg_steps=float(best_avg_steps),
                total_execution_time=float(total_execution_time)
            )
        except Exception as e:
            # En cas d'erreur, retourner des valeurs par défaut
            print(f"Erreur lors de la récupération des statistiques: {e}")
            return StatisticsResponse(
                total_runs=0,
                algorithms=[],
                best_success_rate=0.0,
                best_avg_steps=0.0,
                total_execution_time=0.0
            )
    
    @staticmethod
    def create_saved_model(db: Session, model_data: SavedModelCreate) -> SavedModel:
        """Crée un nouveau modèle sauvegardé"""
        db_model = SavedModel(**model_data.dict())
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model
    
    @staticmethod
    def create_annotation(db: Session, run_id: str, annotation_data: RunAnnotationCreate) -> RunAnnotation:
        """Crée une nouvelle annotation"""
        db_annotation = RunAnnotation(
            run_id=run_id,
            user_id=annotation_data.user_id,
            annotation=annotation_data.annotation,
            tags=annotation_data.tags
        )
        db.add(db_annotation)
        db.commit()
        db.refresh(db_annotation)
        return db_annotation
    
    @staticmethod
    def get_annotations_for_run(db: Session, run_id: str) -> List[RunAnnotation]:
        """Récupère toutes les annotations d'un run"""
        return db.query(RunAnnotation).filter(RunAnnotation.run_id == run_id).order_by(RunAnnotation.created_at).all()
    
    @staticmethod
    def search_runs_by_params(
        db: Session,
        alpha: Optional[float] = None,
        gamma: Optional[float] = None,
        training_runs: Optional[int] = None
    ) -> List[TrainingRun]:
        """Recherche des runs par paramètres spécifiques"""
        query = db.query(TrainingRun)
        
        if alpha is not None:
            query = query.filter(TrainingRun.params['alpha'].astext.cast(float) == alpha)
        if gamma is not None:
            query = query.filter(TrainingRun.params['gamma'].astext.cast(float) == gamma)
        if training_runs is not None:
            query = query.filter(TrainingRun.params['training_runs'].astext.cast(int) == training_runs)
        
        return query.order_by(desc(TrainingRun.created_at)).all()
    
    @staticmethod
    def get_runs_by_date_range(
        db: Session,
        start_date: str,
        end_date: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TrainingRun]:
        """Récupère des runs dans une plage de dates"""
        return db.query(TrainingRun).filter(
            TrainingRun.created_at >= start_date,
            TrainingRun.created_at <= end_date
        ).order_by(desc(TrainingRun.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_training_run(db: Session, run_id: str) -> bool:
        """Supprime un run d'entraînement et ses données associées"""
        run = db.query(TrainingRun).filter(TrainingRun.run_id == run_id).first()
        if run:
            db.delete(run)
            db.commit()
            return True
        return False
    
    @staticmethod
    def compare_runs(db: Session, run_ids: List[str]) -> ComparisonResponse:
        """Compare plusieurs runs d'entraînement"""
        runs = []
        for run_id in run_ids:
            run = DatabaseService.get_training_run(db, run_id)
            if run:
                runs.append(run)
        
        if not runs:
            return ComparisonResponse(runs=[], comparison_metrics={})
        
        # Calcul des métriques de comparaison
        success_rates = []
        avg_steps = []
        execution_times = []
        
        for run in runs:
            if run.test_metrics:
                success_rates.append(run.test_metrics.get("success_rate", 0))
                avg_steps.append(run.test_metrics.get("avg_steps", 0))
            execution_times.append(run.execution_time or 0)
        
        comparison_metrics = {
            "success_rates": success_rates,
            "avg_steps": avg_steps,
            "execution_times": execution_times,
            "best_success_rate": max(success_rates) if success_rates else 0,
            "best_avg_steps": min(avg_steps) if avg_steps else 0,
            "fastest_execution": min(execution_times) if execution_times else 0
        }
        
        return ComparisonResponse(runs=runs, comparison_metrics=comparison_metrics)
