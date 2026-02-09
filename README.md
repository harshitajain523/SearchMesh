# SearchMesh - Federated Search Engine

A federated search engine that aggregates results from Google, Bing, and DuckDuckGo with intelligent deduplication and rule-based filtering.

## Features

- 🔍 **Multi-Source Search**: Query Google, Bing, and DuckDuckGo simultaneously
- 🔄 **Smart Deduplication**: URL normalization + fuzzy title matching
- ⚡ **Concurrent Execution**: Parallel API calls with timeout handling
- 🛡️ **Circuit Breaker**: Graceful degradation when APIs fail
- 🎨 **Modern UI**: Dark theme with glassmorphism effects

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React 18 + TypeScript + Vite
- **Styling**: Vanilla CSS with custom design system
- **State Management**: TanStack Query

## Quick Start

### 1. Clone and Setup

```bash
cd searchmesh
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Run development server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### 4. Docker (Optional)

```bash
# Create .env file with API keys first
docker-compose up --build
```

## Environment Variables

Create a `.env` file in the backend directory:

```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
BING_API_KEY=your_bing_api_key
REDIS_URL=redis://localhost:6379
DEBUG=true
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/search` | GET | Search with query params |
| `/api/v1/search` | POST | Search with JSON body |
| `/api/v1/search/engines` | GET | Get engine status |
| `/api/v1/health` | GET | Health check |
| `/docs` | GET | Swagger documentation |

## Deployment

### Frontend (Vercel)

1. Push to GitHub
2. Import project in Vercel
3. Set root directory to `frontend`
4. Add environment variable `VITE_API_URL` pointing to your backend

### Backend (Railway/Render)

1. Create new project on Railway or Render
2. Set root directory to `backend`
3. Add environment variables (API keys)
4. Deploy

## Project Structure

```
searchmesh/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Config, circuit breaker
│   │   ├── engines/      # Search engine adapters
│   │   ├── dedup/        # Deduplication algorithms
│   │   ├── models/       # Pydantic models
│   │   └── main.py       # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── hooks/        # Custom hooks
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## License

MIT
