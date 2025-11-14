[//]: # (AI-Powered INGRES Support Assistant)
# AI-Powered INGRES Support Assistant

Local RAG Chatbot • Error Analyzer • Log Inspector • JIRA Ticket Automation

A fully local AI-powered support assistant built with FastAPI, FAISS, SentenceTransformers, DialoGPT, and React + TypeScript. Designed to help troubleshoot INGRES database issues using document RAG, error-code intelligence, log parsing, and JIRA ticket automation.

Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quickstart](#quickstart)
  - [Backend (Python)](#backend-python)
  - [Frontend (React)](#frontend-react)
- [API Endpoints](#api-endpoints)
- [RAG & Log Pipeline](#rag--log-pipeline)
- [Ticketing (JIRA)](#ticketing-jira)
- [Development Notes](#development-notes)
- [Contributing](#contributing)
- [License](#license)

Features
- AI Chat (Local LLM): DialoGPT-medium for response generation.
- Retrieval-Augmented Generation (RAG): MiniLM-L6-v2 embeddings + FAISS for local vector search.
- Error & Log Analysis: auto-detect error codes, classify severity, and suggest fixes.
- JIRA Ticket Automation: create tickets from chat, auto-fill metadata and send to JIRA API.

Architecture

React Frontend (Port 8080)  --->  FastAPI Backend (Port 8000)

- Frontend: chat UI, log uploads, ticket dashboard
- Backend: RAG engine, embeddings, local LLM, ticket service, log analyzer

Tech Stack
- Backend: Python 3.10+, FastAPI, FAISS, SentenceTransformers, HuggingFace Transformers, Pydantic
- Frontend: React, TypeScript, Vite, Tailwind CSS, shadcn/ui
- Models: DialoGPT-medium (responses), MiniLM-L6-v2 (embeddings)

Quickstart

Backend (Python)

1. Enter the backend folder and create a virtual environment:

```bash
cd backend
python -m venv venv
```

2. Activate the venv (Windows PowerShell / CMD):

```powershell
.\venv\Scripts\Activate.ps1  # PowerShell
# or
.\venv\Scripts\activate     # CMD
```

If using `bash.exe` (WSL / Git Bash / MinGW) on Windows:

```bash
source venv/Scripts/activate
```

3. Install dependencies and run the backend:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`.

Frontend (React)

1. Enter the frontend folder, install dependencies and run the dev server:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:8080` by default.

API Endpoints

- `GET /` — Health check
- `POST /chat/` — Chat with AI

  Example request body:

  ```json
  { "message": "What is INGRES database?" }
  ```

- `POST /ticket/` — Create a support ticket

  Example request body:

  ```json
  {
    "summary": "Connection timeout",
    "description": "Server not responding",
    "severity": "high"
  }
  ```

RAG & Log Pipeline

- Load INGRES documentation from `data/docs/`.
- Clean and chunk text for embedding.
- Convert chunks to embeddings (MiniLM) and store in FAISS index (`data/embeddings/`).
- At query time, retrieve the top-k chunks and pass context to the local LLM to generate an answer.

Error Code Intelligence

The system recognizes INGRES-style error codes such as `E_US0845`, `E_LQ1040`, `E_DM0042`. For each detected code it attempts to provide:
- Meaning
- Typical cause
- Suggested fix
- Severity level

Log Analysis

Supports uploads of `.txt` / `.log` / server logs / stack traces. The analyzer performs pattern detection, extracts errors, summarizes the issue, and provides recommendations.

Ticketing (JIRA)

The ticketing flow supports creating tickets with auto-filled summary, description, category, and severity. Tickets are stored locally and can be sent to a configured JIRA REST API.

Example JIRA payload:

```json
{
  "fields": {
    "project": { "key": "ING" },
    "summary": "Database timeout issue",
    "description": "Detected error E_DM0042 in logs",
    "issuetype": { "name": "Task" }
  }
}
```

Development Notes

- Embeddings index location: `backend/data/embeddings/faiss.index` (or `data/embeddings/` under project root depending on setup)
- Model files are pulled via HuggingFace — ensure you have network access when first running embedding/LLM model downloads.
- Tests: see `backend/tests/` and top-level `tests/` for evaluation scripts.

Contributing

Feel free to open issues or PRs. Suggested contributions:
- Swap DialoGPT for a newer local LLM (e.g., Mistral, Llama)
- Add conversational memory / session persistence
- Improve multi-user auth and role-based admin features

License

This project does not include a license file by default. Add a `LICENSE` if you intend to publish or share under a specific license.

---

If you'd like, I can also:
- add badges (CI, Python version)
- create a minimal `CONTRIBUTING.md`
- run the backend tests and fix any minor formatting issues

Tell me which of these you'd like next.