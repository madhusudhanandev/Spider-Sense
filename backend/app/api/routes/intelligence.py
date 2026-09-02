"""
GET /api/intelligence/evolution-patterns -- Phase 5.

Deliberately a separate router/prefix from /campaigns rather than nested
under it, to avoid any path-matching ambiguity with GET /campaigns/{id}.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.intelligence import EvolutionPatternsResult
from app.services.intelligence.evolution_patterns_service import compute_evolution_patterns

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.get("/evolution-patterns", response_model=EvolutionPatternsResult)
def evolution_patterns(db: Session = Depends(get_db)):
    return compute_evolution_patterns(db)