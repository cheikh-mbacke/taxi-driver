from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.database import get_db
from app.api.schemas.database import (
    TrainingRun, TrainingRunCreate, TrainingRunSummary,
    SavedModel, SavedModelCreate,
    RunAnnotation, RunAnnotationCreate,
    StatisticsResponse, ComparisonRequest, ComparisonResponse
)
from app.api.services.database_service import DatabaseService

# Database router for all database-related endpoints
database_router = APIRouter()

@database_router.get("/runs", response_model=List[TrainingRunSummary])
async def get_training_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get paginated list of training runs"""
    return DatabaseService.get_training_run_summaries(db, skip=skip, limit=limit)

@database_router.get("/runs/best", response_model=List[TrainingRunSummary])
async def get_best_runs(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get best performing training runs"""
    return DatabaseService.get_best_runs(db, limit=limit)

@database_router.get("/runs/{run_id}", response_model=TrainingRun)
async def get_training_run(run_id: str, db: Session = Depends(get_db)):
    """Get complete details of a specific training run"""
    try:
        run = DatabaseService.get_training_run(db, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Training run not found")
        
        # JSONB returns Python objects directly, no parsing needed
        return run
    except Exception as e:
        print(f"Error retrieving run {run_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving run: {str(e)}")

@database_router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """Get global training statistics"""
    return DatabaseService.get_statistics(db)

@database_router.post("/runs/{run_id}/annotations", response_model=RunAnnotation)
async def add_annotation(
    run_id: str,
    annotation: RunAnnotationCreate,
    db: Session = Depends(get_db)
):
    """Add annotation to a training run"""
    return DatabaseService.create_annotation(db, run_id, annotation)

@database_router.get("/runs/{run_id}/annotations", response_model=List[RunAnnotation])
async def get_annotations_for_run(
    run_id: str,
    db: Session = Depends(get_db)
):
    """Get annotations for a specific training run"""
    return DatabaseService.get_annotations_for_run(db, run_id)

@database_router.get("/runs/search/params")
async def search_runs_by_params(
    alpha: Optional[float] = Query(None),
    gamma: Optional[float] = Query(None),
    training_runs: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Search training runs by specific parameters"""
    return DatabaseService.search_runs_by_params(db, alpha, gamma, training_runs)

@database_router.post("/runs/compare", response_model=ComparisonResponse)
async def compare_runs(
    request: ComparisonRequest,
    db: Session = Depends(get_db)
):
    """Compare multiple training runs"""
    return DatabaseService.compare_runs(db, request.run_ids)

@database_router.delete("/runs/{run_id}")
async def delete_training_run(run_id: str, db: Session = Depends(get_db)):
    """Delete a training run"""
    success = DatabaseService.delete_training_run(db, run_id)
    if not success:
        raise HTTPException(status_code=404, detail="Training run not found")
    return {"message": "Training run deleted successfully"}

@database_router.get("/models", response_model=List[SavedModel])
async def get_saved_models(db: Session = Depends(get_db)):
    """Get list of saved models"""
    # TODO: Implement this functionality
    return []

@database_router.get("/health")
async def database_health_check(db: Session = Depends(get_db)):
    """Database health check endpoint"""
    try:
        # Simple connection test
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "postgresql"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")
