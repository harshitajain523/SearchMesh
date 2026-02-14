# SearchMesh – Federated Search Engine

A pure Software Engineering project that aggregates results from Google and DuckDuckGo, deduplicates them using algorithmic approaches, and enriches image results with Azure Computer Vision.

> **No ML/AI in search logic** – all ranking, deduplication, and filtering is algorithmic.

---

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────┐
│  React UI   │────▶│  FastAPI Backend (async)          │
│  (Vite+TS)  │     │                                  │
└─────────────┘     │  ┌──────────┐  ┌──────────────┐  │
                    │  │  Google   │  │  DuckDuckGo  │  │
                    │  │  Adapter  │  │  Adapter     │  │
                    │  └──────────┘  └──────────────┘  │
                    │                                  │
                    │  ┌──────────────────────────────┐│
                    │  │  Azure Computer Vision       ││
                    │  │  (image enrichment)          ││
                    │  └──────────────────────────────┘│
                    │                                  │
                    │  ┌──────────┐  ┌──────────────┐  │
                    │  │ Dedup    │  │  Circuit      │  │
                    │  │ Engine   │  │  Breaker      │  │
                    │  └──────────┘  └──────────────┘  │
                    └──────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Custom Search API key + Search Engine ID
- Azure Computer Vision key (optional, for image analysis)

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ← add your API keys
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker (full stack)

```bash
docker-compose up --build
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API docs: http://localhost:8000/docs
```

---

## Environment Variables

| Variable                  | Required | Description                     |
| ------------------------- | -------- | ------------------------------- |
| `GOOGLE_API_KEY`          | Yes      | Google Custom Search API key    |
| `GOOGLE_SEARCH_ENGINE_ID` | Yes      | Programmable Search Engine ID   |
| `AZURE_VISION_KEY`        | No       | Azure Computer Vision API key   |
| `AZURE_VISION_ENDPOINT`   | No       | Azure CV endpoint URL           |
| `REDIS_URL`               | No       | Redis URL for caching (Phase 2) |
| `DATABASE_URL`            | No       | PostgreSQL URL (Phase 3)        |
| `DEBUG`                   | No       | Enable debug mode               |

---

## API Endpoints

| Method | Endpoint                                     | Description                 |
| ------ | -------------------------------------------- | --------------------------- |
| GET    | `/api/v1/search?q=query`                     | Federated search            |
| POST   | `/api/v1/search`                             | Search with full options    |
| POST   | `/api/v1/search/analyze-image?image_url=URL` | Azure Vision image analysis |
| GET    | `/api/v1/search/engines`                     | Engine status               |
| GET    | `/api/v1/health`                             | Health check                |

### Search Parameters

```
GET /api/v1/search?q=python+tutorial&sources=google&sources=duckduckgo&max_results=20&dedupe=true
```

---

## Project Structure

```
searchmesh/
├── backend/
│   ├── app/
│   │   ├── api/           # REST endpoints
│   │   ├── core/          # Config, circuit breaker
│   │   ├── engines/       # Search adapters
│   │   │   ├── google.py
│   │   │   ├── duckduckgo.py
│   │   │   ├── azure_vision.py
│   │   │   └── aggregator.py
│   │   ├── dedup/         # URL normalization, fuzzy matching
│   │   ├── models/        # Pydantic schemas
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page views
│   │   ├── hooks/         # Custom hooks
│   │   └── services/      # API client
│   ├── vercel.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Deployment

### Frontend → Vercel

1. Push to GitHub
2. Import in Vercel, set root to `frontend`
3. Set env: `VITE_API_URL=https://your-backend-url/api/v1`

### Backend → Railway / Render

1. Import repo, set root to `backend`
2. Set environment variables
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

---

## Tech Stack

| Layer    | Technology                                            |
| -------- | ----------------------------------------------------- |
| Backend  | Python, FastAPI, httpx, Pydantic                      |
| Frontend | React 18, TypeScript, Vite, TanStack Query            |
| Search   | Google Custom Search, DuckDuckGo (scraping)           |
| Vision   | Azure Computer Vision (tags, captions, OCR)           |
| Infra    | Docker, Vercel, Redis (planned), PostgreSQL (planned) |
