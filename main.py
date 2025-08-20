from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models.database import engine, get_db
from models.job import Base
from api.jobs import router as jobs_router
from api.scheduler import router as scheduler_router
from scheduler.engine import scheduler_engine
import uvicorn

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Task Scheduler API",
    description="A Python-based task scheduler with multiple scheduling algorithms",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
app.include_router(scheduler_router, prefix="/scheduler", tags=["scheduler"])

@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Task Scheduler API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "jobs": "/jobs",
            "scheduler": "/scheduler"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Start the scheduler engine when the application starts"""
    scheduler_engine.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the scheduler engine when the application shuts down"""
    scheduler_engine.stop()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
