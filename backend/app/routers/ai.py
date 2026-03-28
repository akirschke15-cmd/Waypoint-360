import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.config import settings
from app.models.person import Person
from app.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


def _check_api_key():
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI features require ANTHROPIC_API_KEY to be configured",
        )


@router.post("/query")
async def ai_query(
    data: dict,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(get_current_user),
):
    """Natural language query -> LangGraph analysis."""
    _check_api_key()
    from app.ai.service import ai_service

    query = data.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    try:
        result = await ai_service.query(query, db)
        return result
    except Exception as e:
        logger.exception("AI query failed")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.get("/gate-readiness/{gate_id}")
async def gate_readiness(
    gate_id: int,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(get_current_user),
):
    """AI-powered gate readiness assessment."""
    _check_api_key()
    from app.ai.service import ai_service

    try:
        return await ai_service.gate_readiness(gate_id, db)
    except Exception as e:
        logger.exception("Gate readiness analysis failed")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.get("/scope-creep")
async def scope_creep_detection(
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(get_current_user),
):
    """AI-powered scope creep detection across all workstreams."""
    _check_api_key()
    from app.ai.service import ai_service

    try:
        return await ai_service.scope_creep(db)
    except Exception as e:
        logger.exception("Scope creep analysis failed")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.get("/risks/correlated")
async def correlated_risks(
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(get_current_user),
):
    """AI-powered cross-workstream risk correlation."""
    _check_api_key()
    from app.ai.service import ai_service

    try:
        return await ai_service.correlated_risks(db)
    except Exception as e:
        logger.exception("Risk correlation analysis failed")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.get("/summary")
async def executive_summary(
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(get_current_user),
):
    """AI-generated executive program summary."""
    _check_api_key()
    from app.ai.service import ai_service

    try:
        return await ai_service.executive_summary(db)
    except Exception as e:
        logger.exception("Executive summary generation failed")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")
