# ScryTheSpire

ScryTheSpire is a FastAPI backend for Slay the Spire run data. It imports `.RUN` save files from Steam, parses each run's deck, relics, and full act/room history, stores everything in a local database, and serves paginated run data and aggregate statistics through a rate-limited REST API.

## How It Works

The project is broken into three main layers: importing run files, the FastAPI application that serves them, and a shared rate-limiting layer.

### 1. Importing

- **Scripts:** `import_runner.py`, `import_history.py`
- **Function:** Scans Steam save directories for `.RUN` files and parses each run. The Steam path is auto-detected on Windows and can be overridden with the `STEAM_PATH` environment variable. Runs are deduplicated by seed, so re-running the importer is safe. Bad or unparseable files are skipped and the importer keeps going.
- **Parsed data:** deck, relics, and full act/room history per run.
- **Database:** Parsed runs are persisted through the SQLAlchemy models in `models.py`, using the engine/session defined in `database.py`.

### 2. API

- **Entry point:** `main.py`
- **Routes:** `runs.py` (run list/detail), `stats.py` (aggregate statistics)
- **Schemas:** `schemas.py` (Pydantic request/response models)
- **Function:** Serves paginated run data plus win-rate and top-card/relic statistics. Interactive docs are available at `/docs` (Swagger) and `/redoc` (ReDoc).

### 3. Rate Limiting

- **Module:** `rate_limit.py`
- **Function:** A global sliding-window limiter shared across all clients, applied per route group (see the table below). Every response includes `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` headers; `429` responses include `Retry-After`.
- **Disabling:** Set `RATE_LIMIT_DISABLED=1` to turn the limiter off.

## Getting Started

### Prerequisites

- Python 3.x
- Project dependencies (FastAPI, uvicorn, SQLAlchemy)

### Running

From the backend terminal:

```bash
uvicorn main:app --reload
```

Swagger is served at `/docs` and ReDoc at `/redoc`.

## API

### Runs

| Endpoint | Description |
|---|---|
| `GET /api/runs` | Paginated list of runs |
| `GET /api/runs/{id}` | Single run with deck + relics |

### Stats

| Endpoint | Description |
|---|---|
| `GET /api/stats/characterWinrate` | Win rate by character |
| `GET /api/stats/topCards` | Most-picked cards |
| `GET /api/stats/cardWinrate` | Win rate by card |
| `GET /api/stats/topRelics` | Most-picked relics |
| `GET /api/stats/relicWinrate` | Win rate by relic |

### Other

| Endpoint | Description |
|---|---|
| `GET /api/health` | Health check; never rate-limited |

Swagger at `/docs`, ReDoc at `/redoc`.

## Rate Limits

Global sliding window, shared across all clients:

| Group | Limit | Notes |
|---|---|---|
| `runs_list` | 60 req / 60s | |
| `runs_detail` | 120 req / 60s | |
| `stats` | 30 req / 60s | all stats endpoints combined |

Every response includes `X-RateLimit-Limit` / `-Remaining` / `-Reset`; `429` responses include `Retry-After`. Disable the limiter with `RATE_LIMIT_DISABLED=1`.

## Project Structure

```
backend/
├── main.py          # FastAPI app entry point
├── runs.py          # Routes for /runs
├── stats.py         # Routes for /stats
├── schemas.py       # Pydantic models (request/response)
├── database.py      # SQLAlchemy engine & session
├── models.py        # SQLAlchemy models
├── rate_limit.py    # sliding window limiter
├── import_runner.py # parse_run_data
└── import_history.py
```

## Known Gaps

- Stats aggregate all characters together (no `?character=` filter yet)
- Abandoned runs count in win-rate denominators
- `minPicks=0` default lets 1-pick cards show 100%
- `/api/runs` returns full detail on list (no summary/detail split)
- No filtering on the runs list (character, victory, ascension, date)
- No write endpoints; import is script-only
- No frontend yet