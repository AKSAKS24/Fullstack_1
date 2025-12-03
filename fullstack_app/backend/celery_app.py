"""
Celery application setup.  This file configures the Celery instance and registers tasks.

Celery is used here for executing long‑running agent tasks in the background.  The
broker and result backend default to Redis but can be configured via environment
variables.  See `SETUP.md` for details on running the worker.
"""
import os
from celery import Celery


def make_celery() -> Celery:
    broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    result_backend = os.environ.get("CELERY_RESULT_BACKEND", broker_url)
    celery = Celery(
        "ai_agents",
        broker=broker_url,
        backend=result_backend,
        include=["src.tasks"],
    )

    # Optional Celery configuration can be set here or via env vars
    celery.conf.update({
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
        "timezone": "UTC",
        "enable_utc": True,
    })
    return celery


celery_app = make_celery()