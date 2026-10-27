# ScryTheSpire

in backend terminal
uvicorn main:app --reload

## features

- imports .RUN files from steam saves (auto-detects steam path on windows, override with STEAM_PATH)
- dedupes by seed, safe to re-run
- skips bad files, keeps going
- parses deck, relics, full act/room history per run

## api

runs
- GET /api/runs            # paginated list
- GET /api/runs/{id}       # single run w/ deck + relics

stats
- GET /api/stats/characterWinrate
- GET /api/stats/topCards
- GET /api/stats/cardWinrate
- GET /api/stats/topRelics
- GET /api/stats/relicWinrate

other
- GET /api/health          # never rate-limited

swagger at /docs, redoc at /redoc

## rate limit

global sliding window, shared across all clients

- runs_list    60 req / 60s
- runs_detail  120 req / 60s
- stats        30 req / 60s (all endpoints combined)

every response has X-RateLimit-Limit / -Remaining / -Reset
429 comes with Retry-After

disable with RATE_LIMIT_DISABLED=1

## structure

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

## known gaps

- stats aggregate all characters together (no ?character= filter yet)
- abandoned runs count in winrate denominators
- minPicks=0 default lets 1-pick cards show 100%
- /api/runs returns full detail on list (no summary/detail split)
- no filtering on runs list (character, victory, ascension, date)
- no write endpoints, import is script-only
- no frontend yet