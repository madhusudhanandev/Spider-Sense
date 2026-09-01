from fastapi import APIRouter

from app.api.routes import analysis, health, incidents, reports

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(analysis.router)
api_router.include_router(incidents.router)
api_router.include_router(reports.router)
