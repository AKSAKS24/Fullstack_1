from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api import chat, agents, jobs, files


def create_app() -> FastAPI:
    """
    Factory function to create the FastAPI application.
    """
    # Load environment variables from .env if present
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except Exception:
        pass
    app = FastAPI(
        title="AI Agents Backend",
        description="FastAPI backend for chat completion and modular agents",
        version="0.1.0",
    )

    # CORS configuration – update origins list as needed
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static directory for serving generated files (e.g., DOCX outputs)
    app.mount("/static", StaticFiles(directory="generated_files"), name="static")

    # Include routers
    app.include_router(chat.router, prefix="/chat", tags=["Chat"])
    app.include_router(agents.router, prefix="/agent", tags=["Agents"])
    app.include_router(jobs.router, prefix="/job", tags=["Jobs"])
    app.include_router(files.router, prefix="/files", tags=["Files"])

    return app


app = create_app()