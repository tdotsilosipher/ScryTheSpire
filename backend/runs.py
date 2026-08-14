# backend/runs.py
# 100 per page design

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from models import Run as RunModel
from schemas import Run

router = APIRouter(prefix="/runs", tags=["runs"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[Run])
def list_runs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    runs = db.query(RunModel).offset(skip).limit(limit).all()
    return runs

@router.get("/{run_id}", response_model=Run)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(RunModel).filter(RunModel.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run