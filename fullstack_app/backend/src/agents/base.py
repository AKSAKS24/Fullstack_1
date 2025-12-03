"""
Base classes and utilities for agents.  All agent classes should inherit from
`BaseAgent` and override the `run` coroutine.  The base class provides helper
methods for reading RAG files, calling language models, and updating job progress.
"""
import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles

from ..services.job_manager import job_manager, JobStatus
from ..models.providers import get_model
from ..utils.document_extractor import extract_text_from_files
from ..utils.docx_builder import DocxBuilder


class BaseAgent(ABC):
    """
    Abstract base class for all agents.  Subclasses must implement `run`, which
    orchestrates the agent's workflow given input text and/or files.
    """
    name: str = "base"
    description: str = ""
    rag_path: Path = Path(__file__).resolve().parent / "rag"

    def __init__(self) -> None:
        # Preload RAG assets if they exist
        self.sections_def: Optional[List[Dict[str, Any]]] = None
        sections_file = self.rag_path / "sections.json"
        if sections_file.exists():
            with open(sections_file, "r", encoding="utf-8") as f:
                self.sections_def = json.load(f)
        self.guidelines: Optional[str] = None
        guidelines_file = self.rag_path / "guidelines.md"
        if guidelines_file.exists():
            with open(guidelines_file, "r", encoding="utf-8") as f:
                self.guidelines = f.read()
        self.formatting: Optional[Dict[str, Any]] = None
        fmt_file = self.rag_path / "formatting.json"
        if fmt_file.exists():
            with open(fmt_file, "r", encoding="utf-8") as f:
                self.formatting = json.load(f)

    async def update_progress(self, job_id: str, message: str) -> None:
        """
        Append a progress log to the specified job.
        """
        await job_manager.update_job(job_id, JobStatus.RUNNING, log=message)

    async def call_llm(self, prompt: str, model_name: str = "gpt-3.5-turbo", stream: bool = False) -> str:
        """
        Call the configured language model provider with the given prompt.  This
        helper hides the details of the underlying provider and returns a string
        result.  Streaming is not implemented here; streaming occurs at the
        HTTP layer in the chat API.
        """
        model = get_model(model_name)
        # Each provider should expose an async `generate` function returning text
        text = await model.generate(prompt)
        return text

    async def run(self, job_id: str, input_text: Optional[str], files: Optional[List[Dict[str, str]]]) -> Any:
        """
        Main entry point for the agent.  Subclasses must override this
        coroutine to implement their specific logic.  The base class
        implementation just returns the input text or extracted text from
        files.
        """
        raise NotImplementedError