from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models import Program, Gate, Workstream

router = APIRouter()


@router.get("/")
async def get_program(db: AsyncSession = Depends(get_db)):
    """Get the full program overview. No auth required for initial load."""
    result = await db.execute(
        select(Program)
        .options(
            selectinload(Program.phases),
            selectinload(Program.gates).selectinload(Gate.exit_criteria),
            selectinload(Program.workstreams),
        )
        .limit(1)
    )
    program = result.scalar_one_or_none()
    if not program:
        return {"error": "No program found. Run seed."}

    return {
        "id": program.id,
        "name": program.name,
        "description": program.description,
        "status": program.status.value if program.status else None,
        "phases": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "start_week": p.start_week,
                "end_week": p.end_week,
                "goal": p.goal,
            }
            for p in sorted(program.phases, key=lambda x: x.sort_order)
        ],
        "gates": [
            {
                "id": g.id,
                "name": g.name,
                "short_name": g.short_name,
                "week_number": g.week_number,
                "status": g.status.value if g.status else None,
                "exit_criteria": [
                    {"id": ec.id, "description": ec.description, "status": ec.status.value if ec.status else None}
                    for ec in sorted(g.exit_criteria, key=lambda x: x.sort_order)
                ],
            }
            for g in sorted(program.gates, key=lambda x: x.sort_order)
        ],
        "workstreams": [
            {
                "id": w.id,
                "name": w.name,
                "short_name": w.short_name,
                "status": w.status.value if w.status else None,
                "purpose": w.purpose,
            }
            for w in sorted(program.workstreams, key=lambda x: x.sort_order)
        ],
    }


@router.post("/seed")
async def seed_program(db: AsyncSession = Depends(get_db)):
    """Trigger database seeding from PDF data. Open for initial setup."""
    from app.db.seed import seed_waypoint_data

    await seed_waypoint_data(db)
    return {"status": "seeded", "message": "Waypoint program data loaded from Commercial Workshop PDF"}
