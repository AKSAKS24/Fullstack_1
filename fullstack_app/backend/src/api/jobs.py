"""
Job status API.  The frontend queries this endpoint to obtain the status of
background tasks such as agent execution.  Supports optional Server‑Sent Events
for live updates.
"""
from typing import AsyncGenerator, Dict, Optional

import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

from ..services.job_manager import job_manager


router = APIRouter()


@router.get("/{job_id}")
async def get_job_status(job_id: str, stream: bool = False):
    """
    Return the current status of a job.  If `stream` is true, stream updates
    whenever the job changes.  Streaming terminates when the job completes or
    fails.
    """
    job = await job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if stream:
        async def event_generator() -> AsyncGenerator[str, None]:
            current_logs_len = 0
            while True:
                job_state = await job_manager.get_job(job_id)
                if not job_state:
                    break
                # Send new log lines as they appear
                logs = job_state["logs"]
                if len(logs) > current_logs_len:
                    for line in logs[current_logs_len:]:
                        yield f"data: {line}\n\n"
                    current_logs_len = len(logs)
                if job_state["status"] in ("completed", "failed"):
                    # Final state; send result as a final event
                    import json
                    # Send final state as JSON string inside SSE data field
                    payload = json.dumps({"status": job_state["status"], "result": job_state["result"]})
                    yield f"data: {payload}\n\n"
                    break
                await asyncio.sleep(0.5)
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        return JSONResponse(job)