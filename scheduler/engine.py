import threading
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.job import Job, JobStatus, SchedulingAlgorithm
from models.database import SessionLocal
from .algorithms import SchedulerFactory, RoundRobinScheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobExecutor:
    """Handles the execution of individual jobs"""
    
    def __init__(self, job: Job, db: Session):
        self.job = job
        self.db = db
        self.thread = None
        self.is_running = False
        
    def execute(self):
        """Execute the job in a separate thread"""
        self.is_running = True
        self.thread = threading.Thread(target=self._run_job)
        self.thread.start()
        
    def _run_job(self):
        """Internal method to run the job"""
        try:
            # Update job status to running
            self.job.status = JobStatus.RUNNING
            self.job.started_at = datetime.now()
            self.db.commit()
            
            logger.info(f"Starting job {self.job.id}: {self.job.name}")
            
            # Simulate job execution
            time.sleep(self.job.execution_time)
            
            # Update job status to completed
            self.job.status = JobStatus.COMPLETED
            self.job.completed_at = datetime.now()
            self.job.result = f"Job {self.job.name} completed successfully"
            self.db.commit()
            
            logger.info(f"Completed job {self.job.id}: {self.job.name}")
            
        except Exception as e:
            # Update job status to failed
            self.job.status = JobStatus.FAILED
            self.job.error_message = str(e)
            self.db.commit()
            logger.error(f"Failed job {self.job.id}: {self.job.name} - {e}")
            
        finally:
            self.is_running = False
            
    def stop(self):
        """Stop the job execution"""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)

class SchedulerEngine:
    """Main scheduler engine that manages job execution with multithreading"""
    
    def __init__(self):
        self.is_running = False
        self.schedulers: Dict[SchedulingAlgorithm, object] = {}
        self.active_executors: Dict[int, JobExecutor] = {}
        self.scheduler_thread = None
        self.lock = threading.Lock()
        
    def start(self):
        """Start the scheduler engine"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
            
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.start()
        logger.info("Scheduler engine started")
        
    def stop(self):
        """Stop the scheduler engine"""
        self.is_running = False
        
        # Stop all active executors
        with self.lock:
            for executor in self.active_executors.values():
                executor.stop()
            self.active_executors.clear()
            
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            
        logger.info("Scheduler engine stopped")
        
    def add_job(self, job: Job):
        """Add a job to the appropriate scheduler"""
        with self.lock:
            if job.algorithm not in self.schedulers:
                self.schedulers[job.algorithm] = SchedulerFactory.create_scheduler(job.algorithm)
            
            self.schedulers[job.algorithm].add_job(job)
            logger.info(f"Added job {job.id} to {job.algorithm.value} scheduler")
            
    def remove_job(self, job: Job):
        """Remove a job from the scheduler"""
        with self.lock:
            if job.algorithm in self.schedulers:
                self.schedulers[job.algorithm].remove_job(job)
                
            # If job is currently executing, stop it
            if job.id in self.active_executors:
                self.active_executors[job.id].stop()
                del self.active_executors[job.id]
                
    def get_status(self) -> Dict:
        """Get current scheduler status"""
        with self.lock:
            active_count = len(self.active_executors)
            pending_count = sum(len(scheduler.jobs) for scheduler in self.schedulers.values())
            
            return {
                "is_running": self.is_running,
                "active_jobs": active_count,
                "pending_jobs": pending_count,
                "schedulers": {algo.value: len(scheduler.jobs) for algo, scheduler in self.schedulers.items()}
            }
            
    def _scheduler_loop(self):
        """Main scheduler loop that runs in a separate thread"""
        while self.is_running:
            try:
                self._process_jobs()
                time.sleep(1)  # Check for new jobs every second
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(5)  # Wait longer on error
                
    def _process_jobs(self):
        """Process jobs from all schedulers"""
        with self.lock:
            # Check for completed jobs
            completed_jobs = []
            for job_id, executor in self.active_executors.items():
                if not executor.is_running:
                    completed_jobs.append(job_id)
                    
            # Remove completed jobs
            for job_id in completed_jobs:
                del self.active_executors[job_id]
                
            # Start new jobs if we have capacity
            max_concurrent_jobs = 3  # Limit concurrent jobs
            if len(self.active_executors) < max_concurrent_jobs:
                self._start_next_job()
                
    def _start_next_job(self):
        """Start the next available job"""
        db = SessionLocal()
        try:
            # Try to get a job from each scheduler
            for algorithm, scheduler in self.schedulers.items():
                job = scheduler.get_next_job()
                if job:
                    # Check if job is still pending
                    db.refresh(job)
                    if job.status == JobStatus.PENDING:
                        # Create executor and start job
                        executor = JobExecutor(job, db)
                        self.active_executors[job.id] = executor
                        executor.execute()
                        logger.info(f"Started job {job.id} with {algorithm.value} algorithm")
                        break
                        
        except Exception as e:
            logger.error(f"Error starting job: {e}")
        finally:
            db.close()

# Global scheduler engine instance
scheduler_engine = SchedulerEngine()
