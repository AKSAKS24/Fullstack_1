"""
Agent orchestration endpoints.  Exposes a list of available agents and an endpoint
to trigger agent execution via the background job system.  Agent run requests
create a job and dispatch it to Celery.
"""
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..services.job_manager import job_manager
from ..agents import load_agent
from ..tasks import run_agent_task


router = APIRouter()


class AgentRunRequest(BaseModel):
    agent: str
    input_text: Optional[str] = None
    files: Optional[List[Dict[str, str]]] = None


@router.get("/list")
async def list_agents():
    """
    Return a list of available agents by introspecting the `src/agents` package.
    """
    # Discover agent packages by scanning the filesystem
    import pkg_resources
    import pkgutil
    import importlib
    import os
    package_dir = os.path.dirname(__file__)
    agents_dir = os.path.join(package_dir, "..", "agents")
    agents_list = []
    for finder, name, ispkg in pkgutil.iter_modules([agents_dir]):
        if ispkg and not name.startswith("__"):
            # Attempt to load agent.json for metadata
            try:
                module = importlib.import_module(f"src.agents.{name}.agent")
                agent_cls = getattr(module, "Agent")
                agents_list.append({"name": agent_cls.name, "description": getattr(agent_cls, "description", "")})
            except Exception:
                pass
    return JSONResponse({"agents": agents_list})


@router.post("/run")
async def run_agent(request: AgentRunRequest):
    """
    Trigger an agent execution.  A job is created and dispatched to the Celery
    worker; the job ID is returned to the client for polling.
    """
    # Validate agent existence
    try:
        load_agent(request.agent)
    except ValueError:
        raise HTTPException(status_code=404, detail="Agent not found")
    # Create job
    job_id = await job_manager.create_job(job_type=request.agent, description=f"Run agent {request.agent}")
    # Kick off Celery task
    run_agent_task.delay(job_id, request.agent, request.input_text, request.files)
    return JSONResponse({"job_id": job_id})