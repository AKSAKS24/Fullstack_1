"""
Simple in-memory job manager to track asynchronous tasks.  Each job is represented by a
dictionary with an ID, status, logs, and result.  This module is designed to work
alongside Celery tasks or FastAPI background tasks.  In production, consider persisting
jobs in a database or using a proper result backend.
"""
import asyncio
import uuid
from typing import Any, Dict, Optional


class JobStatus:
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobManager:
    def __init__(self) -> None:
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def create_job(self, job_type: str, description: str = "") -> str:
        job_id = str(uuid.uuid4())
        async with self._lock:
            self._jobs[job_id] = {
                "id": job_id,
                "type": job_type,
                "description": description,
                "status": JobStatus.QUEUED,
                "logs": [],
                "result": None,
            }
        return job_id

    async def update_job(self, job_id: str, status: str, log: Optional[str] = None, result: Any = None) -> None:
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job["status"] = status
            if log:
                job["logs"].append(log)
            if result is not None:
                job["result"] = result

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            return self._jobs.get(job_id)


# Instantiate a global job manager
job_manager = JobManager()