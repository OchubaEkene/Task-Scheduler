from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .job import JobStatus, SchedulingAlgorithm

class JobBase(BaseModel):
    name: str
    description: Optional[str] = None
    priority: int = 1
    execution_time: int
    algorithm: SchedulingAlgorithm = SchedulingAlgorithm.FIFO

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    execution_time: Optional[int] = None
    algorithm: Optional[SchedulingAlgorithm] = None

class JobResponse(JobBase):
    id: int
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class SchedulerStatus(BaseModel):
    is_running: bool
    active_jobs: int
    pending_jobs: int
    completed_jobs: int
    failed_jobs: int
    current_algorithm: Optional[str] = None
