from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.sql import func
from .database import Base
import enum

class JobStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class SchedulingAlgorithm(enum.Enum):
    FIFO = "fifo"
    ROUND_ROBIN = "round_robin"
    SJF = "sjf"
    PRIORITY = "priority"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    priority = Column(Integer, default=1)
    execution_time = Column(Integer)  # in seconds
    algorithm = Column(Enum(SchedulingAlgorithm), default=SchedulingAlgorithm.FIFO)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
