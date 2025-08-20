# Task Scheduler

A Python-based task scheduler that implements multiple scheduling algorithms with a REST API for job management.

## Features

- **Multiple Scheduling Algorithms:**
  - FIFO (First In, First Out)
  - Round Robin
  - SJF (Shortest Job First)
  - Priority-based scheduling

- **Advanced Features:**
  - Priority queues for efficient job management
  - Multithreading for concurrent job execution
  - REST API for job management
  - SQLite persistence for job data
  - Real-time job status monitoring

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application

```bash
python main.py
```

The application will start on `http://localhost:8000`

### API Endpoints

- `GET /jobs` - List all jobs
- `POST /jobs` - Create a new job
- `GET /jobs/{job_id}` - Get job details
- `PUT /jobs/{job_id}` - Update job
- `DELETE /jobs/{job_id}` - Delete job
- `GET /scheduler/status` - Get scheduler status
- `POST /scheduler/start` - Start the scheduler
- `POST /scheduler/stop` - Stop the scheduler

### Job Creation Example

```bash
curl -X POST "http://localhost:8000/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Data Processing Task",
    "priority": 5,
    "execution_time": 30,
    "algorithm": "priority"
  }'
```

## Architecture

- `scheduler/` - Core scheduling algorithms and logic
- `api/` - REST API endpoints
- `models/` - Data models and database schema
- `utils/` - Utility functions and helpers

## Scheduling Algorithms

1. **FIFO**: Jobs are executed in the order they arrive
2. **Round Robin**: Jobs are executed in time slices, cycling through all jobs
3. **SJF**: Jobs with shortest execution time are prioritized
4. **Priority**: Jobs are executed based on their priority level (higher priority first)
