from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.person import Person

router = APIRouter()


@router.get("/me")
async def get_current_user():
    """Stub -- returns default admin user for v1."""
    return {
        "id": 1,
        "name": "Alex Kirschke",
        "email": "alex.kirschke@wnco.com",
        "role": "admin",
        "title": "AgentOps Lead",
    }


@router.post("/login")
async def login():
    """Stub -- JWT auth to be implemented."""
    return {
        "access_token": "stub-token-v1",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "name": "Alex Kirschke",
            "role": "admin",
        },
    }
