"""
Projects Router with strict multi-tenant organization isolation and RBAC permission checks.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, log_audit_event, require_permission

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[schemas.ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Project)
    if current_user.org_id:
        query = query.filter(models.Project.org_id == current_user.org_id)
    return query.all()


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = db.get(models.Project, project_id)
    if not project or (current_user.org_id and project.org_id != current_user.org_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("", response_model=schemas.ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: schemas.ProjectIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("project:create")),
):
    project = models.Project(
        org_id=current_user.org_id,
        name=payload.name,
        lead=payload.lead,
        deadline=payload.deadline,
        progress=payload.progress,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    log_audit_event(
        db,
        action="project_created",
        resource_type="project",
        resource_id=project.id,
        actor=current_user,
        details={"name": project.name, "lead": project.lead},
    )
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_permission("project:delete")),
):
    project = db.get(models.Project, project_id)
    if not project or (current_user.org_id and project.org_id != current_user.org_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    db.delete(project)
    db.commit()

    log_audit_event(
        db,
        action="project_deleted",
        resource_type="project",
        resource_id=project_id,
        actor=current_user,
    )
    return None
