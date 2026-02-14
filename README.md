# SearchMesh

A federated search aggregation platform that queries multiple search providers concurrently, deduplicates results algorithmically, and enriches image content through Azure Computer Vision.

---

## Architecture

SearchMesh is built on a layered, async-first architecture.

```
Client (React/TS)
  |
  v
API Gateway (FastAPI)
  |
  +-- Search Aggregator (asyncio.gather)
  |     +-- Google Custom Search Adapter
  |     +-- DuckDuckGo Adapter
  |
  +-- Deduplication Engine
  |     +-- URL Normalizer
  |     +-- Fuzzy Matcher (Jaccard Similarity)
  |
  +-- Azure Computer Vision (image enrichment)
  |
  +-- Circuit Breaker Registry
```

**Search Aggregator** dispatches queries to all configured providers in parallel, collects partial results on failure, and enforces per-engine timeouts.

**Deduplication Engine** normalizes URLs (stripping tracking parameters, sorting query strings, unifying protocols) then applies Jaccard similarity on tokenized titles to surface and merge near-duplicates.

**Circuit Breaker** tracks failure rates per provider and transitions between closed, open, and half-open states to prevent cascading failures.

**Azure Computer Vision** optionally analyzes image results, appending tags, captions, OCR text, and dimension metadata.

---

## API

| Method | Endpoint                                       | Description                     |
| ------ | ---------------------------------------------- | ------------------------------- |
| `GET`  | `/api/v1/search?q=<query>`                     | Federated search                |
| `POST` | `/api/v1/search`                               | Search with filters and options |
| `POST` | `/api/v1/search/analyze-image?image_url=<url>` | Image analysis via Azure CV     |
| `GET`  | `/api/v1/search/engines`                       | Provider health and status      |
| `GET`  | `/api/v1/health`                               | System health                   |

---

## Stack

| Layer            | Technology                            |
| ---------------- | ------------------------------------- |
| Backend          | Python 3.11, FastAPI, httpx, Pydantic |
| Frontend         | React 18, TypeScript, Vite            |
| Search Providers | Google Custom Search API, DuckDuckGo  |
| Image Analysis   | Azure Computer Vision                 |
| Infrastructure   | Docker, Docker Compose                |

---

## License

Open source.
