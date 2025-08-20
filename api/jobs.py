from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.database import get_db
from models.job import Job, JobStatus
from models.schemas import JobCreate, JobUpdate, JobResponse
from scheduler.engine import scheduler_engine

router = APIRouter()

@router.get("/", response_model=List[JobResponse])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all jobs with pagination"""
    jobs = db.query(Job).offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job by ID"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Create a new job"""
    db_job = Job(
        name=job.name,
        description=job.description,
        priority=job.priority,
        execution_time=job.execution_time,
        algorithm=job.algorithm
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    # Add job to scheduler
    scheduler_engine.add_job(db_job)
    
    return db_job

@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, job_update: JobUpdate, db: Session = Depends(get_db)):
    """Update an existing job"""
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Only allow updates if job is not running
    if db_job.status == JobStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Cannot update running job")
    
    # Update fields
    update_data = job_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_job, field, value)
    
    db.commit()
    db.refresh(db_job)
    
    # Update job in scheduler if algorithm changed
    if 'algorithm' in update_data:
        scheduler_engine.remove_job(db_job)
        scheduler_engine.add_job(db_job)
    
    return db_job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job"""
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Remove from scheduler
    scheduler_engine.remove_job(db_job)
    
    # Delete from database
    db.delete(db_job)
    db.commit()
    
    return None

@router.post("/{job_id}/cancel", response_model=JobResponse)
def cancel_job(job_id: int, db: Session = Depends(get_db)):
    """Cancel a running job"""
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if db_job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
        raise HTTPException(status_code=400, detail="Job cannot be cancelled")
    
    # Remove from scheduler
    scheduler_engine.remove_job(db_job)
    
    # Update status
    db_job.status = JobStatus.CANCELLED
    db.commit()
    db.refresh(db_job)
    
    return db_job

@router.get("/status/{job_id}")
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """Get detailed status of a job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": job.id,
        "name": job.name,
        "status": job.status.value,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "result": job.result,
        "error_message": job.error_message
    }
