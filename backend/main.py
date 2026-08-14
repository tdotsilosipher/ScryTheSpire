# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from runs import router as runs_router
from stats import router as stats_router

app = FastAPI(title="Scry The Spire")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs_router, prefix="/api")
app.include_router(stats_router, prefix="/api")

@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Backend is running"}