# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is an AI-powered chatbot system for INGRES database support, featuring:
- **Backend**: Python FastAPI with RAG (Retrieval-Augmented Generation) using OpenAI embeddings and FAISS vector search
- **Frontend**: React TypeScript with Vite, shadcn/ui components, and TanStack Query
- **Architecture**: Microservice-style separation with chat, ticket management, and document ingestion services

## Development Commands

### Backend (Python FastAPI)
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run document ingestion (required before first use)
python -m scripts.ingest_docs

# Start development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest app/tests/

# Run single test
pytest app/tests/test_app_smoke.py::test_health
```

### Frontend (React TypeScript)
```bash
# Navigate to frontend directory 
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Build for development
npm run build:dev

# Lint code
npm run lint

# Preview production build
npm run preview
```

### Docker
```bash
# Build backend container
cd backend && docker build -t ai-chatbot-backend .

# Run backend container (requires env vars)
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key ai-chatbot-backend
```

## Architecture Overview

### Backend Structure
- **`app/main.py`**: FastAPI application entry point with CORS middleware
- **`app/api/`**: API route handlers for chat and ticket endpoints
- **`app/services/`**: Core business logic
  - `rag_pipeline.py`: OpenAI embeddings + FAISS vector search + GPT-4 completion
  - `ingestion.py`: Document processing (PDF/text) and vector index creation
  - `ticket_service.py`: Support ticket management
- **`app/models/`**: Pydantic data models for request/response validation
- **`app/utils/`**: Configuration and logging utilities
- **`scripts/ingest_docs.py`**: Standalone script for document ingestion

### Frontend Structure
- **`src/components/chat/`**: Chat interface components (messages, input, sidebar)
- **`src/services/`**: API service layers for backend communication
- **`src/pages/`**: Route components (main chat interface, tickets, 404)
- **`src/components/ui/`**: shadcn/ui component library implementation

### Data Flow
1. **Document Ingestion**: `data/docs/` → chunking → OpenAI embeddings → FAISS index → `data/embeddings/`
2. **Chat Query**: User input → vector similarity search → context retrieval → OpenAI chat completion → response
3. **Ticket Creation**: Chat context → ticket service → structured ticket data

### Key Dependencies
- **Backend**: FastAPI, OpenAI API, FAISS (CPU), SQLAlchemy, Alembic, PyPDF2
- **Frontend**: React 18, TypeScript, Vite, TanStack Query, shadcn/ui, Tailwind CSS

## Environment Setup

### Required Environment Variables (.env in backend/)
```bash
OPENAI_API_KEY=sk-...  # Required for embeddings and chat completion
JIRA_API_TOKEN=        # Optional for JIRA ticket integration  
JIRA_BASE_URL=         # Optional
JIRA_PROJECT_KEY=      # Optional
FRONTEND_ORIGIN=*      # CORS origin (defaults to *)
```

### Document Ingestion Setup
1. Place documentation files (PDF, TXT) in `backend/data/docs/`
2. Run `python -m scripts.ingest_docs` to create vector index
3. Vector embeddings stored in `backend/data/embeddings/faiss.index`

## Development Workflow

### Adding New Features
1. **Backend API**: Add routes in `app/api/`, business logic in `app/services/`
2. **Frontend Services**: Add API client in `src/services/`
3. **UI Components**: Extend existing chat components or create new ones
4. **Testing**: Add tests in `app/tests/` for backend functionality

### Working with RAG System
- Documents automatically chunked into ~800 token pieces with 100 token overlap
- Uses `text-embedding-3-small` model for embeddings (1536 dimensions)
- FAISS IndexFlatL2 for similarity search (top-k=4 retrieval)
- GPT-4o-mini for response generation with retrieved context

### Frontend Development Notes
- Uses React Router for navigation between chat and tickets
- TanStack Query for API state management
- shadcn/ui components with custom styling
- Error code detection and analysis built into chat interface
- File upload capability for log analysis

### Database Integration
- SQLAlchemy ORM with Alembic for migrations
- Models defined in `app/models/` for users and chat history
- Currently using basic in-memory storage for tickets (extend for production)

## Common Debugging

### Backend Issues
- **Empty responses**: Ensure `data/docs/` contains files and ingestion completed
- **OpenAI errors**: Verify API key and model availability
- **Import errors**: Check Python path includes app module

### Frontend Issues  
- **API connection**: Verify backend running on port 8000
- **Build errors**: Check TypeScript strict mode configurations
- **Styling issues**: Tailwind classes defined in `tailwind.config.ts`

### Vector Search Issues
- **No results**: Re-run document ingestion after adding new docs
- **Poor relevance**: Adjust chunk size/overlap in `ingestion.py`
- **Index corruption**: Delete `data/embeddings/` and re-ingest

## Testing Considerations

### Backend Testing
- Smoke tests verify API health endpoints
- RAG pipeline testing requires mocked OpenAI responses
- Integration tests need vector index fixture data

### Frontend Testing
- Component testing with React Testing Library
- API mocking for service layer tests
- E2E testing for complete chat workflows