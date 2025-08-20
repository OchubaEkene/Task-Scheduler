import heapq
import time
from typing import List, Optional, Callable
from queue import Queue, PriorityQueue
from models.job import Job, JobStatus, SchedulingAlgorithm
from datetime import datetime

class BaseScheduler:
    """Base class for all scheduling algorithms"""
    
    def __init__(self):
        self.jobs = []
        self.current_job = None
        
    def add_job(self, job: Job):
        """Add a job to the scheduler"""
        self.jobs.append(job)
        
    def get_next_job(self) -> Optional[Job]:
        """Get the next job to execute"""
        raise NotImplementedError
        
    def remove_job(self, job: Job):
        """Remove a job from the scheduler"""
        if job in self.jobs:
            self.jobs.remove(job)

class FIFOScheduler(BaseScheduler):
    """First In, First Out scheduler using a simple queue"""
    
    def __init__(self):
        super().__init__()
        self.queue = Queue()
        
    def add_job(self, job: Job):
        """Add job to FIFO queue"""
        self.queue.put(job)
        
    def get_next_job(self) -> Optional[Job]:
        """Get next job from queue (FIFO order)"""
        if not self.queue.empty():
            return self.queue.get()
        return None
        
    def remove_job(self, job: Job):
        """Remove job from queue (not efficient for FIFO)"""
        # For FIFO, we typically don't remove jobs from middle
        pass

class RoundRobinScheduler(BaseScheduler):
    """Round Robin scheduler with time quantum"""
    
    def __init__(self, time_quantum: int = 10):
        super().__init__()
        self.time_quantum = time_quantum
        self.queue = Queue()
        self.current_job = None
        self.remaining_time = 0
        
    def add_job(self, job: Job):
        """Add job to round robin queue"""
        self.queue.put(job)
        
    def get_next_job(self) -> Optional[Job]:
        """Get next job with time quantum consideration"""
        if self.current_job and self.remaining_time > 0:
            return self.current_job
            
        if not self.queue.empty():
            self.current_job = self.queue.get()
            self.remaining_time = min(self.time_quantum, self.current_job.execution_time)
            return self.current_job
            
        return None
        
    def update_remaining_time(self, executed_time: int):
        """Update remaining time for current job"""
        self.remaining_time -= executed_time
        if self.remaining_time <= 0 and self.current_job:
            # Job completed or time quantum expired
            if self.current_job.execution_time > 0:
                # Job not completed, add back to queue
                self.queue.put(self.current_job)
            self.current_job = None

class SJFScheduler(BaseScheduler):
    """Shortest Job First scheduler using priority queue"""
    
    def __init__(self):
        super().__init__()
        self.priority_queue = PriorityQueue()
        
    def add_job(self, job: Job):
        """Add job to priority queue (execution_time as priority)"""
        # Lower execution time = higher priority
        self.priority_queue.put((job.execution_time, job.id, job))
        
    def get_next_job(self) -> Optional[Job]:
        """Get job with shortest execution time"""
        if not self.priority_queue.empty():
            return self.priority_queue.get()[2]  # Return the job object
        return None

class PriorityScheduler(BaseScheduler):
    """Priority-based scheduler using priority queue"""
    
    def __init__(self):
        super().__init__()
        self.priority_queue = PriorityQueue()
        
    def add_job(self, job: Job):
        """Add job to priority queue (priority as key)"""
        # Higher priority = lower number (higher priority)
        # Use negative priority so higher priority jobs come first
        self.priority_queue.put((-job.priority, job.id, job))
        
    def get_next_job(self) -> Optional[Job]:
        """Get job with highest priority"""
        if not self.priority_queue.empty():
            return self.priority_queue.get()[2]  # Return the job object
        return None

class SchedulerFactory:
    """Factory class to create scheduler instances"""
    
    @staticmethod
    def create_scheduler(algorithm: SchedulingAlgorithm, **kwargs):
        """Create a scheduler based on the algorithm type"""
        if algorithm == SchedulingAlgorithm.FIFO:
            return FIFOScheduler()
        elif algorithm == SchedulingAlgorithm.ROUND_ROBIN:
            time_quantum = kwargs.get('time_quantum', 10)
            return RoundRobinScheduler(time_quantum)
        elif algorithm == SchedulingAlgorithm.SJF:
            return SJFScheduler()
        elif algorithm == SchedulingAlgorithm.PRIORITY:
            return PriorityScheduler()
        else:
            raise ValueError(f"Unknown scheduling algorithm: {algorithm}")
