"""
Project Simulation & ML Risk Router:
- "What-If" Discrete-Event Schedule Simulator
- Machine Learning Risk Prediction & XAI Factor Breakdown
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.services import ml_risk_service

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


@router.post("/what-if", response_model=schemas.SimulationOut)
def run_what_if_simulation(
    scenario: schemas.SimulationIn,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Simulate project delivery timeline shifts based on developer availability, scope changes, or added resources."""
    return ml_risk_service.simulate_project_scenario(db, scenario)


@router.get("/critical-path")
def get_critical_path(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Compute topological Critical Path Method (CPM) schedule, early/late dates, and slack."""
    tasks = db.query(models.Task).all()
    return ml_risk_service.calculate_cpm_schedule(tasks)


@router.get("/risk/{task_id}", response_model=schemas.MlRiskPredictionOut)
def get_task_ml_risk(
    task_id: str,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Get machine learning predictive risk score and explainable contributing factors (XAI)."""
    return ml_risk_service.predict_task_risk(db, task_id)

