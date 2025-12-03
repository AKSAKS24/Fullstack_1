# FullStack AI Agents Application

This repository contains a full‑stack application that demonstrates how modular AI agents can be orchestrated through a chat UI.  The system is composed of a FastAPI backend with asynchronous architecture, a Celery background job system backed by Redis, and a React + Vite frontend.  Two example agents are implemented: a **SAP Technical Specification Document (TSD) generator** and a **SAP ABAP code generator**.  The application is designed to be extensible, allowing new agents and model providers to be plugged in easily.

## Directory Structure

```
fullstack_app/
├── architecture.md          # Mermaid diagrams of the system
├── SETUP.md                 # Step‑by‑step setup instructions
├── README.md                # This file
├── backend/                 # FastAPI backend with Celery and agents
│   ├── requirements.txt     # Python dependencies
│   ├── src/
│   │   ├── main.py          # Application factory
│   │   ├── api/             # API routers (chat, agents, jobs, files)
│   │   ├── agents/          # Agent implementations and RAG
│   │   ├── models/          # Model provider abstraction (OpenAI)
│   │   ├── services/        # Job manager
│   │   ├── utils/           # Document extraction and DOCX builder
│   │   └── tasks.py         # Celery tasks
│   ├── celery_app.py        # Celery configuration
│   └── generated_files/     # Output documents served via /static
├── frontend/                # React + Vite frontend
│   ├── package.json         # npm dependencies and scripts
│   ├── vite.config.js       # Proxy configuration for API
│   ├── index.html           # HTML entry point
│   └── src/
│       ├── App.jsx          # Root React component
│       ├── main.jsx         # ReactDOM renderer
│       ├── services/api.js  # API wrapper functions
│       ├── styles/app.css   # Basic styling
│       └── ...              # Other directories prepared for future expansion
└── slides/                  # (if present) placeholder for optional presentation assets
```

For detailed setup instructions, see [SETUP.md](./SETUP.md).  Architectural diagrams are provided in [architecture.md](./architecture.md).  The backend README in `backend/README.md` contains an overview of backend features.