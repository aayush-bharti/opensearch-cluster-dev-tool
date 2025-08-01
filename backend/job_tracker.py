# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import os
import threading
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import logging
from constants import ErrorMessages

logger = logging.getLogger(__name__)

# Job status constants
class JobStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Task status constants
class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

# Job tracker class
class JobTracker:
    """Simple job tracking system with file-based persistence."""
    
    def __init__(self, jobs_dir: str = "job_data"):
        # Convert to absolute path immediately to be immune to working directory changes
        self.jobs_dir = os.path.abspath(jobs_dir)
        self.lock = threading.Lock()
        
        # Create jobs directory if it doesn't exist
        os.makedirs(self.jobs_dir, exist_ok=True)
        
        # Clean up any jobs that were running when server was restarted
        self.cleanup_interrupted_jobs()
        
        logger.info(f"JobTracker initialized with absolute jobs directory: {self.jobs_dir}")
    
    # cleanup the interrupted jobs
    def cleanup_interrupted_jobs(self) -> None:
        """Clean up jobs that were running when the server was restarted."""
        try:
            cleaned_jobs = 0
            for filename in os.listdir(self.jobs_dir):
                if filename.endswith('.json'):
                    job_id = filename[:-5]
                    job_data = self.load_job(job_id)
                    if job_data and self.is_job_interrupted(job_data):
                        self.mark_job_as_interrupted(job_id, job_data)
                        cleaned_jobs += 1
            
            if cleaned_jobs > 0:
                logger.info(f"Cleaned up {cleaned_jobs} interrupted jobs from previous server session")
        except Exception as e:
            logger.error(f"Failed to cleanup interrupted jobs: {e}")

    # check if a job was interrupted
    def is_job_interrupted(self, job_data: Dict[str, Any]) -> bool:
        """Check if a job was interrupted using process validation and time-based checks."""
        job_status = job_data.get("status")
        
        # If job is not running/queued, it can't be interrupted
        if job_status not in ["running", "queued"]:
            return False
        
        # Check if the actual process is still running
        process_id = job_data.get("process_id")
        if process_id:
            try:
                # Check if process exists
                os.kill(process_id, 0)
                # Process is alive, allow to continue
                logger.info(f"Job {job_data.get('job_id')} process {process_id} is still running")
                return False
            except OSError:
                # Process is dead, mark as interrupted
                logger.warning(f"Job {job_data.get('job_id')} process {process_id} is dead")
                return True
        
        # Fallback: time-based validation if no process ID
        started_at = job_data.get("started_at")
        if started_at:
            try:
                start_time = datetime.fromisoformat(started_at)
                current_time = datetime.now()
                time_diff = (current_time - start_time).total_seconds()
                
                # If job has been running for more than 2 hours, mark as interrupted
                if time_diff > 7200:
                    logger.warning(f"Job {job_data.get('job_id')} has been running for {time_diff/3600:.1f} hours - marking as interrupted")
                    return True
                
                # For jobs running less than 2 hours, allow to continue
                logger.info(f"Job {job_data.get('job_id')} has been running for {time_diff/60:.1f} minutes - allowing to continue")
                return False
                
            except Exception as e:
                # If can't parse the time, assume interrupted
                logger.error(f"Error parsing job start time: {e}")
                return True
        
        # If no start time, assume interrupted (inconsistent state)
        logger.warning(f"Job {job_data.get('job_id')} has no start time - marking as interrupted")
        return True
    
    # mark a job as interrupted
    def mark_job_as_interrupted(self, job_id: str, job_data: Dict[str, Any]) -> None:
        """Mark a job and its running tasks as failed due to server restart."""
        # Update overall job status
        job_data["status"] = JobStatus.FAILED.value
        job_data["error"] = ErrorMessages.WORKFLOW_INTERRUPTED
        
        if not job_data.get("completed_at"):
            job_data["completed_at"] = datetime.now().isoformat()
        
        # Update any running tasks to failed
        for task_name, task_data in job_data.get("tasks", {}).items():
            if task_data.get("status") in ["running", "pending"]:
                task_data["status"] = TaskStatus.FAILED.value
                task_data["error"] = ErrorMessages.WORKFLOW_INTERRUPTED
                if not task_data.get("completed_at"):
                    task_data["completed_at"] = datetime.now().isoformat()
        
        # Clear current task and update progress
        job_data["current_task"] = None
        job_data["progress"]["current_step"] = ErrorMessages.WORKFLOW_INTERRUPTED
        
        self.save_job(job_id, job_data)
        logger.info(f"Marked interrupted job {job_id} as failed")
    
    # get the job file
    def get_job_file(self, job_id: str) -> str:
        """Get the file path for a job."""
        return os.path.join(self.jobs_dir, f"{job_id}.json")
    
    # create a new job
    def create_job(self, config: Dict[str, Any], tasks: Dict[str, bool]) -> str:
        """Create a new job and return its ID."""
        job_id = str(uuid.uuid4())
        
        # Initialize task statuses
        task_statuses = {}
        for task_name, enabled in tasks.items():
            if enabled:
                task_statuses[task_name] = {
                    "status": TaskStatus.PENDING.value,
                    "started_at": None,
                    "completed_at": None,
                    "result": None,
                    "error": None
                }
        
        job_data = {
            "job_id": job_id,
            "status": JobStatus.QUEUED.value,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "config": config,
            "tasks": task_statuses,
            "current_task": None,
            "progress": {
                "total_tasks": len(task_statuses),
                "completed_tasks": 0,
                "current_step": "Initializing..."
            },
            "workflow_timestamp": None,
            "results": {},
            "error": None,
            "process_id": None
        }
        
        with self.lock:
            self.save_job(job_id, job_data)
        
        logger.info(f"Created job {job_id} with tasks: {list(task_statuses.keys())}")
        return job_id
    
    # save the job data to file
    def save_job(self, job_id: str, job_data: Dict[str, Any]) -> None:
        """Save job data to file."""
        job_file = self.get_job_file(job_id)
        with open(job_file, 'w') as f:
            json.dump(job_data, f, indent=2)
    
    # load the job data from file
    def load_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Load job data from file."""
        job_file = self.get_job_file(job_id)
        if not os.path.exists(job_file):
            return None
        
        try:
            with open(job_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load job {job_id}: {e}")
            return None
    
    # get the current job status
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current job status."""
        with self.lock:
            return self.load_job(job_id)
    
    # update the overall job status
    def update_job_status(self, job_id: str, status: JobStatus, error: str = None) -> bool:
        """Update overall job status."""
        with self.lock:
            job_data = self.load_job(job_id)
            if not job_data:
                return False
            
            job_data["status"] = status.value
            
            if status == JobStatus.RUNNING and not job_data["started_at"]:
                job_data["started_at"] = datetime.now().isoformat()
                 # Set process ID when job starts
                job_data["process_id"] = os.getpid()
            elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                job_data["completed_at"] = datetime.now().isoformat()
                # Clear process ID when job ends
                job_data["process_id"] = None
            
            if error:
                job_data["error"] = error
            
            self.save_job(job_id, job_data)
            logger.info(f"Updated job {job_id} status to {status.value}")
            return True
    
    # update the status of a specific task
    def update_task_status(self, job_id: str, task_name: str, status: TaskStatus, 
                          result: Dict[str, Any] = None, error: str = None) -> bool:
        """Update status of a specific task."""
        with self.lock:
            job_data = self.load_job(job_id)
            if not job_data or task_name not in job_data["tasks"]:
                return False
            
            task_data = job_data["tasks"][task_name]
            task_data["status"] = status.value
            
            if status == TaskStatus.RUNNING and not task_data["started_at"]:
                task_data["started_at"] = datetime.now().isoformat()
                job_data["current_task"] = task_name
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                task_data["completed_at"] = datetime.now().isoformat()
                
                if status == TaskStatus.COMPLETED:
                    job_data["progress"]["completed_tasks"] += 1
                    if result:
                        task_data["result"] = result
                        job_data["results"][task_name] = result
                
                if error:
                    task_data["error"] = error
                
                # Update current task to next pending task or None if all done
                pending_tasks = [name for name, data in job_data["tasks"].items() 
                               if data["status"] == TaskStatus.PENDING.value]
                job_data["current_task"] = pending_tasks[0] if pending_tasks else None
            
            self.save_job(job_id, job_data)
            logger.info(f"Updated job {job_id} task {task_name} status to {status.value}")
            return True
    
    # update the current progress step
    def update_progress(self, job_id: str, step: str) -> bool:
        """Update current progress step."""
        with self.lock:
            job_data = self.load_job(job_id)
            if not job_data:
                return False
            
            job_data["progress"]["current_step"] = step
            self.save_job(job_id, job_data)
            return True
    
    # set the workflow timestamp for the job
    def set_workflow_timestamp(self, job_id: str, timestamp: str) -> bool:
        """Set the workflow timestamp for the job."""
        with self.lock:
            job_data = self.load_job(job_id)
            if not job_data:
                return False
            
            job_data["workflow_timestamp"] = timestamp
            self.save_job(job_id, job_data)
            return True
    
    # list the recent jobs
    def list_jobs(self, limit: int = 50) -> list:
        """List recent jobs."""
        jobs = []
        try:
            for filename in os.listdir(self.jobs_dir):
                if filename.endswith('.json'):
                    job_id = filename[:-5]
                    job_data = self.load_job(job_id)
                    if job_data:
                        jobs.append({
                            "job_id": job_id,
                            "display_id": job_data.get("display_id", 0),
                            "status": job_data["status"],
                            "created_at": job_data["created_at"],
                            "tasks": list(job_data["tasks"].keys()),
                            "progress": job_data["progress"]
                        })
            
            # Sort by creation time (newest first)
            jobs.sort(key=lambda x: x["created_at"], reverse=True)
            
            # Assign sequential display IDs if they don't exist
            for i, job in enumerate(jobs):
                if job["display_id"] == 0:
                    job["display_id"] = i + 1
            
            return jobs[:limit]
        
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            return []
    
    # delete a job
    def delete_job(self, job_id: str) -> bool:
        """Delete a job by ID."""
        job_file = self.get_job_file(job_id)
        if os.path.exists(job_file):
            os.remove(job_file)
            logger.info(f"Deleted job {job_id}")
            return True
        else:
            logger.warning(f"Tried to delete job {job_id} but it doesn't exist")
            return False

    # cleanup the old jobs
    def cleanup_old_jobs(self, days_old: int = 7) -> int:
        """Clean up job files older than specified days."""
        import time
        
        cleaned = 0
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        
        try:
            for filename in os.listdir(self.jobs_dir):
                if filename.endswith('.json'):
                    job_file = os.path.join(self.jobs_dir, filename)
                    if os.path.getmtime(job_file) < cutoff_time:
                        os.remove(job_file)
                        cleaned += 1
                        logger.info(f"Cleaned up old job file: {filename}")
        
        except Exception as e:
            logger.error(f"Failed to cleanup old jobs: {e}")
        
        return cleaned

# Global job tracker instance
job_tracker = JobTracker()
