from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="spider-twin-agent", version="0.1.0")
app.include_router(router)


@app.get("/")
def root() -> dict:
    return {"message": "spider-twin-agent is running"}
