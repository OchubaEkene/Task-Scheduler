from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.job import Job, JobStatus
from models.schemas import SchedulerStatus
from scheduler.engine import scheduler_engine

router = APIRouter()

@router.get("/status", response_model=SchedulerStatus)
def get_scheduler_status(db: Session = Depends(get_db)):
    """Get current scheduler status"""
    status_info = scheduler_engine.get_status()
    
    # Get job counts by status
    active_jobs = db.query(Job).filter(Job.status == JobStatus.RUNNING).count()
    pending_jobs = db.query(Job).filter(Job.status == JobStatus.PENDING).count()
    completed_jobs = db.query(Job).filter(Job.status == JobStatus.COMPLETED).count()
    failed_jobs = db.query(Job).filter(Job.status == JobStatus.FAILED).count()
    
    return SchedulerStatus(
        is_running=status_info["is_running"],
        active_jobs=active_jobs,
        pending_jobs=pending_jobs,
        completed_jobs=completed_jobs,
        failed_jobs=failed_jobs,
        current_algorithm=None  # Could be enhanced to show current algorithm
    )

@router.post("/start")
def start_scheduler():
    """Start the scheduler engine"""
    try:
        scheduler_engine.start()
        return {"message": "Scheduler started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")

@router.post("/stop")
def stop_scheduler():
    """Stop the scheduler engine"""
    try:
        scheduler_engine.stop()
        return {"message": "Scheduler stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")

@router.get("/jobs/active")
def get_active_jobs(db: Session = Depends(get_db)):
    """Get currently active jobs"""
    active_jobs = db.query(Job).filter(Job.status == JobStatus.RUNNING).all()
    return [
        {
            "id": job.id,
            "name": job.name,
            "algorithm": job.algorithm.value,
            "started_at": job.started_at,
            "execution_time": job.execution_time
        }
        for job in active_jobs
    ]

@router.get("/jobs/pending")
def get_pending_jobs(db: Session = Depends(get_db)):
    """Get pending jobs"""
    pending_jobs = db.query(Job).filter(Job.status == JobStatus.PENDING).all()
    return [
        {
            "id": job.id,
            "name": job.name,
            "algorithm": job.algorithm.value,
            "priority": job.priority,
            "execution_time": job.execution_time,
            "created_at": job.created_at
        }
        for job in pending_jobs
    ]

@router.get("/jobs/completed")
def get_completed_jobs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Get recently completed jobs"""
    completed_jobs = db.query(Job).filter(Job.status == JobStatus.COMPLETED).order_by(Job.completed_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": job.id,
            "name": job.name,
            "algorithm": job.algorithm.value,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "result": job.result
        }
        for job in completed_jobs
    ]

@router.get("/jobs/failed")
def get_failed_jobs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Get failed jobs"""
    failed_jobs = db.query(Job).filter(Job.status == JobStatus.FAILED).order_by(Job.completed_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": job.id,
            "name": job.name,
            "algorithm": job.algorithm.value,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "error_message": job.error_message
        }
        for job in failed_jobs
    ]

@router.post("/jobs/clear-completed")
def clear_completed_jobs(db: Session = Depends(get_db)):
    """Clear all completed jobs"""
    try:
        deleted_count = db.query(Job).filter(Job.status == JobStatus.COMPLETED).delete()
        db.commit()
        return {"message": f"Cleared {deleted_count} completed jobs"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear completed jobs: {str(e)}")

@router.post("/jobs/clear-failed")
def clear_failed_jobs(db: Session = Depends(get_db)):
    """Clear all failed jobs"""
    try:
        deleted_count = db.query(Job).filter(Job.status == JobStatus.FAILED).delete()
        db.commit()
        return {"message": f"Cleared {deleted_count} failed jobs"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear failed jobs: {str(e)}")
