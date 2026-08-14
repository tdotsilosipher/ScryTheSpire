# ScryTheSpire

in backend terminal
uvicorn main:app --reload
backend/
├── main.py          # FastAPI app entry point
├── runs.py          # Routes for /runs
├── stats.py         # Routes for /stats
├── schemas.py       # Pydantic models (request/response)
├── database.py      # SQLAlchemy engine & session
├── models.py        # SQLAlchemy models
├── import_runner.py # parse_run_data (optional for imports)
└── import_history.py