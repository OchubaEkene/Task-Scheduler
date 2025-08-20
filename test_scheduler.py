#!/usr/bin/env python3
"""
Test script for the Task Scheduler
Demonstrates different scheduling algorithms
"""

import requests
import time
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def create_job(name, priority, execution_time, algorithm):
    """Create a new job"""
    job_data = {
        "name": name,
        "description": f"Test job for {algorithm} algorithm",
        "priority": priority,
        "execution_time": execution_time,
        "algorithm": algorithm
    }
    
    response = requests.post(f"{BASE_URL}/jobs", json=job_data)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Failed to create job: {response.text}")
        return None

def get_jobs():
    """Get all jobs"""
    response = requests.get(f"{BASE_URL}/jobs")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get jobs: {response.text}")
        return []

def get_scheduler_status():
    """Get scheduler status"""
    response = requests.get(f"{BASE_URL}/scheduler/status")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get scheduler status: {response.text}")
        return None

def main():
    """Main test function"""
    print("=== Task Scheduler Test ===\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("Server is not running. Please start the server first:")
            print("python main.py")
            return
    except requests.exceptions.ConnectionError:
        print("Cannot connect to server. Please start the server first:")
        print("python main.py")
        return
    
    print("Server is running. Starting tests...\n")
    
    # Test 1: FIFO Algorithm
    print("1. Testing FIFO Algorithm")
    print("-" * 30)
    
    jobs = [
        ("FIFO Job 1", 1, 5, "fifo"),
        ("FIFO Job 2", 1, 3, "fifo"),
        ("FIFO Job 3", 1, 7, "fifo"),
    ]
    
    for name, priority, exec_time, algo in jobs:
        job = create_job(name, priority, exec_time, algo)
        if job:
            print(f"Created: {job['name']} (ID: {job['id']})")
    
    print("\n2. Testing Priority Algorithm")
    print("-" * 30)
    
    jobs = [
        ("Priority Job 1", 3, 5, "priority"),
        ("Priority Job 2", 1, 3, "priority"),  # Higher priority
        ("Priority Job 3", 5, 7, "priority"),  # Lower priority
    ]
    
    for name, priority, exec_time, algo in jobs:
        job = create_job(name, priority, exec_time, algo)
        if job:
            print(f"Created: {job['name']} (ID: {job['id']}, Priority: {priority})")
    
    print("\n3. Testing SJF Algorithm")
    print("-" * 30)
    
    jobs = [
        ("SJF Job 1", 1, 8, "sjf"),
        ("SJF Job 2", 1, 2, "sjf"),  # Shortest job
        ("SJF Job 3", 1, 6, "sjf"),
    ]
    
    for name, priority, exec_time, algo in jobs:
        job = create_job(name, priority, exec_time, algo)
        if job:
            print(f"Created: {job['name']} (ID: {job['id']}, Time: {exec_time}s)")
    
    print("\n4. Testing Round Robin Algorithm")
    print("-" * 30)
    
    jobs = [
        ("RR Job 1", 1, 10, "round_robin"),
        ("RR Job 2", 1, 5, "round_robin"),
        ("RR Job 3", 1, 8, "round_robin"),
    ]
    
    for name, priority, exec_time, algo in jobs:
        job = create_job(name, priority, exec_time, algo)
        if job:
            print(f"Created: {job['name']} (ID: {job['id']}, Time: {exec_time}s)")
    
    print("\n=== Job Status ===")
    print("Waiting for jobs to process...")
    
    # Monitor jobs for a while
    for i in range(10):
        time.sleep(2)
        status = get_scheduler_status()
        if status:
            print(f"Active: {status['active_jobs']}, Pending: {status['pending_jobs']}, "
                  f"Completed: {status['completed_jobs']}, Failed: {status['failed_jobs']}")
    
    print("\n=== Final Job List ===")
    jobs = get_jobs()
    for job in jobs:
        print(f"ID: {job['id']}, Name: {job['name']}, Status: {job['status']}, "
              f"Algorithm: {job['algorithm']}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
