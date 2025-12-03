"""
API routers are defined in separate modules and imported here for easy inclusion in the FastAPI app.
"""
from .chat import router as chat_router  # noqa
from .agents import router as agents_router  # noqa
from .jobs import router as jobs_router  # noqa
from .files import router as files_router  # noqa