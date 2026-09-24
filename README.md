# AI-Powered Incident Management & Operations Platform

A comprehensive incident management system featuring AI-powered diagnosis using RAG (Retrieval Augmented Generation), built with FastAPI, PostgreSQL, and Ollama.

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Phases](#project-phases)
- [Development](#development)
- [Testing](#testing)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Browser / Client                        │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                   Streamlit UI (Port 8501)                   │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│              FastAPI REST API (Port 8000)                    │
│  - Authentication (JWT)                                     │
│  - Incident CRUD                                            │
│  - AI Analysis Orchestration                                │
│  - Audit Logging                                            │
└─────────────────────────────────────────────────────────────┘
        │                           │                   │
        │                           │                   │
    ┌───▼────────┐         ┌────────▼─────┐      ┌─────▼──────────┐
    │ PostgreSQL │         │  RAG Engine   │      │  Ollama LLM    │
    │ (Port 5432)│         │  - FAISS      │      │ (Port 11434)   │
    │            │         │  - Embeddings │      │                │
    │ - Users    │         │  - Vector DB  │      │ - mistral      │
    │ - Incidents│         │                │      │ - llama3       │
    │ - Analyses │         │                │      │                │
    │ - Audit    │         │                │      │                │
    └────────────┘         └────────────────┘      └────────────────┘
```

## Prerequisites

- **Docker & Docker Compose** (v24+)
- **Python 3.11+** (for local development)
- **Git**
- **4GB+ RAM** (for Ollama and database)

## Quick Start

### 1. Clone and Setup Environment

```bash
git clone <repo-url>
cd incident-platform

# Copy environment template
cp .env.example .env

# Update .env with your configuration (optional for dev)
```

### 2. Start Services with Docker Compose

```bash
docker-compose up -d
```

This starts:
- **PostgreSQL** on port 5432
- **Ollama** on port 11434 (pulls model on first run)
- **FastAPI Backend** on port 8000
- **Streamlit Frontend** on port 8501

### 3. Verify Services

```bash
# Check backend health
curl http://localhost:8000/health

# Check Ollama
curl http://localhost:11434/api/tags

# Access Streamlit
open http://localhost:8501

# View API docs
open http://localhost:8000/docs
```

## Project Phases

### Phase 1: Foundation ✅
- Repository structure
- Environment configuration
- Database setup (async SQLAlchemy + PostgreSQL)
- Core models (User, Incident, AIAnalysis, AuditLog)
- FastAPI foundation with health check

**Current Status**: Phase 1 Complete
- Database async engine configured
- All models defined
- Docker Compose ready
- Health endpoint working

### Phase 2: Authentication & CRUD (Next)
- JWT authentication router
- User registration/login
- Incident CRUD endpoints
- Audit logging service
- Input validation

### Phase 3: RAG & AI Engine
- Knowledge base ingestion script
- FAISS vector store setup
- Sentence Transformers embeddings
- Ollama integration
- AI analysis service

### Phase 4: Frontend Dashboard
- Streamlit UI
- Authentication UI
- Incident management interface
- Analysis visualization
- Audit log viewer

### Phase 5: Testing & Deployment
- Pytest suite (unit & integration)
- Docker image optimization
- GitHub Actions CI/CD pipeline
- Security scanning

### Phase 6: Production Ready
- Cloud deployment guide (Azure)
- Monitoring and observability
- Performance optimization
- Documentation

## Development

### Local Setup (Without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Start PostgreSQL locally (example: brew services start postgresql@14)

# Run migrations/init (Phase 2)

# Start FastAPI dev server
cd backend
uvicorn app.main:app --reload
```

### Environment Variables

Key variables in `.env`:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (min 32 chars)
- `OLLAMA_BASE_URL`: Ollama service URL
- `OLLAMA_MODEL`: Model to use (mistral, llama3)
- `FAISS_INDEX_PATH`: Vector store location

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest app/tests/test_health.py -v
```

## API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
incident-platform/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, DB, security
│   │   ├── db/             # Models
│   │   ├── schemas/        # Pydantic validators
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── tests/          # Pytest suite
│   │   └── main.py         # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   └── streamlit_app.py
├── rag/
│   ├── ingest.py           # Knowledge base ingestion
│   └── vector_store/       # FAISS indices
├── knowledge_base/         # Docs & troubleshooting
├── docker-compose.yml
├── .env.example
└── README.md
```

## Stack Summary

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend Framework | FastAPI | 0.104+ |
| Database ORM | SQLAlchemy | 2.0+ |
| Database | PostgreSQL | 16 |
| Auth | JWT (PyJWT) | 2.8+ |
| Password Hashing | Bcrypt (Passlib) | 1.7+ |
| Embeddings | Sentence-Transformers | 2.2+ |
| Vector Store | FAISS | 1.7+ |
| LLM Runtime | Ollama | latest |
| Frontend | Streamlit | 1.28+ |
| Testing | Pytest | 7.4+ |
| Containerization | Docker | 24+ |
| CI/CD | GitHub Actions | - |

## Logging

Logs are configured to INFO level by default. Set `LOG_LEVEL=DEBUG` for verbose output.

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f ollama
```

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process on port
lsof -i :8000  # FastAPI
lsof -i :5432  # PostgreSQL
lsof -i :11434 # Ollama
lsof -i :8501  # Streamlit
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

### Ollama Model Not Loading
```bash
# Pull model manually
docker exec incident-ollama ollama pull mistral

# List available models
docker exec incident-ollama ollama list
```

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/name`
4. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue or contact the team.

---

**Phase 1 Status**: ✅ Complete
- Next: Phase 2 (Authentication & CRUD endpoints)