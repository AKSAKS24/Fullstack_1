# Architecture Diagrams

Below are Mermaid diagrams that illustrate the high‑level architecture and the sequence of operations in the AI agents platform.

## Overall System

```mermaid
graph TD
  subgraph Frontend
    UI[React UI]
    UI --> APICalls[Axios API Calls]
  end
  subgraph Backend
    API[FastAPI Application]
    Jobs[Job Manager]
    Celery[Celery Worker]
    Agents[Agent Modules]
    Models[Model Providers]
    Storage[File Storage]
    RAG[Knowledge Files]
    APICalls --> API
    API --> Jobs
    API --> Celery
    Celery --> Agents
    Agents --> RAG
    Agents --> Models
    Models --> Providers
    Celery --> Jobs
    Jobs --> API
    API --> Storage
  end
  subgraph Broker
    Redis[Redis Broker]
  end
  API --> Redis
  Celery --> Redis
  Jobs --> Redis
```

The frontend interacts with the FastAPI backend via HTTP.  Heavy tasks are queued into Celery using a Redis broker.  Agents read from their RAG folders and call the configured model providers.  Generated documents are saved to the file storage directory and served via the `/static` route.

## TSD Agent Execution Sequence

```mermaid
sequenceDiagram
  participant User
  participant Frontend
  participant FastAPI
  participant JobManager
  participant CeleryWorker
  participant TSD_Agent
  participant LLM
  participant Storage

  User->>Frontend: Select TSD agent, upload files, send request
  Frontend->>FastAPI: POST /agent/run
  FastAPI->>JobManager: create job record
  FastAPI->>CeleryWorker: enqueue run_agent_task(job_id, tsd, ...)
  CeleryWorker->>TSD_Agent: run(job_id, input_text, files)
  loop For each section
    TSD_Agent->>JobManager: update progress
    TSD_Agent->>LLM: generate section content
    LLM-->>TSD_Agent: content
  end
  TSD_Agent->>Storage: build DOCX file
  TSD_Agent->>JobManager: mark job completed with file URL
  Frontend->>FastAPI: GET /job/{job_id}?stream=true
  FastAPI->>Frontend: SSE progress logs and final result
```

This sequence covers the asynchronous execution of the TSD agent.  The ABAP agent follows a similar pattern but returns text instead of a document.