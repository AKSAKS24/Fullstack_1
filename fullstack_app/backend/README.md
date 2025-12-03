# FullStack AI Agents Backend

This backend is built with **FastAPI** and designed for extensibility and scalability.  It provides RESTful and streaming endpoints for normal chat completion, agent-driven workflows, file uploads and extraction, background job management, and integration with different language model providers.  Agents encapsulate domain‑specific logic such as generating SAP TSD documents or ABAP code.

## Key Features

* **Async First** – all routes and services use asynchronous functions for maximum throughput.
* **Agent Architecture** – plug‑in multiple agents, each with its own RAG (retrieval‑augmented generation) folder and metadata (`agent.json`).
* **Background Processing** – tasks are executed via Celery with a Redis broker and results backend; jobs expose IDs, statuses, logs and results.
* **Dynamic Model Selection** – choose between different model providers at runtime (OpenAI, Anthropic, etc.).
* **Document Extraction** – safely parse PDF, DOCX, TXT, and CSV files with proper MIME type validation.
* **DOCX Assembly** – assemble sectioned documents using `python‑docx` for the TSD agent.
* **Streaming** – support Server‑Sent Events (SSE) for token streaming and job progress updates.

## Development Setup

See `../SETUP.md` in the project root for instructions on installing dependencies, configuring environment variables, and running the backend server and Celery worker.