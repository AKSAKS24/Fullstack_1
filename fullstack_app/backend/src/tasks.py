"""
Celery tasks for executing agents.  Each task is responsible for running an agent and
updating the job manager with progress.  Tasks must catch exceptions and update
job status accordingly.
"""
import asyncio
import os
from typing import Dict, List, Optional

from celery import shared_task

from .services.job_manager import job_manager, JobStatus
from .agents import load_agent


@shared_task(bind=True)
def run_agent_task(self, job_id: str, agent_name: str, input_text: Optional[str], files: Optional[List[Dict[str, str]]]) -> None:
    """
    Celery task that runs a specified agent.

    Args:
        job_id: Job identifier created by the JobManager.
        agent_name: Name of the agent to execute.
        input_text: User provided input text (may be None if files supplied).
        files: List of file metadata dicts with `path` keys.
    """
    # Mark job as running
    asyncio.run(job_manager.update_job(job_id, JobStatus.RUNNING, log=f"Starting agent '{agent_name}'"))
    try:
        agent_cls = load_agent(agent_name)
        agent = agent_cls()
        # The agent `run` method is asynchronous; call it via asyncio.run
        result = asyncio.run(agent.run(job_id=job_id, input_text=input_text, files=files))
        # Save result: for TSD agent this may be a file path; for ABAP agent it may be text
        asyncio.run(job_manager.update_job(job_id, JobStatus.COMPLETED, log="Agent completed", result=result))
    except Exception as exc:
        # Capture exception and update job as failed
        asyncio.run(job_manager.update_job(job_id, JobStatus.FAILED, log=str(exc), result=None))
        # Re‑raise for Celery logging
        raise exc