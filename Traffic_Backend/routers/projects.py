from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from .. import db_config, models

router = APIRouter(prefix="/projects", tags=["projects"])


def get_db():
    db = db_config.SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ProjectCreate(BaseModel):
    name: str
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    start_lat: Optional[float] = None
    start_lon: Optional[float] = None
    end_lat: Optional[float] = None
    end_lon: Optional[float] = None
    resource_allocation: Optional[str] = None
    emission_reduction_estimate: Optional[float] = None


class ProjectUpdate(BaseModel):
    name: Optional[str]
    status: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    start_lat: Optional[float]
    start_lon: Optional[float]
    end_lat: Optional[float]
    end_lon: Optional[float]
    resource_allocation: Optional[str]
    emission_reduction_estimate: Optional[float]


class ProjectOut(BaseModel):
    id: int
    name: str
    status: str

    class Config:
        orm_mode = True


@router.post("/", response_model=dict)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = models.Project(
        name=payload.name,
        status=payload.status,
        start_time=payload.start_time,
        end_time=payload.end_time,
        start_lat=payload.start_lat,
        start_lon=payload.start_lon,
        end_lat=payload.end_lat,
        end_lon=payload.end_lon,
        resource_allocation=payload.resource_allocation,
        emission_reduction_estimate=payload.emission_reduction_estimate
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"message": "Project created", "id": project.id}


@router.get("/", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(models.Project).all()
    return projects


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=dict)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(project, field, value)
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"message": "Project updated", "id": project.id}


@router.delete("/{project_id}", response_model=dict)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted", "id": project_id}
