from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.models import Dependency, Workstream

router = APIRouter()


@router.get("/")
async def list_dependencies(db: AsyncSession = Depends(get_db)):
    """Full dependency graph data for D3 visualization."""
    ws_result = await db.execute(select(Workstream).order_by(Workstream.sort_order))
    workstreams = ws_result.scalars().all()

    dep_result = await db.execute(
        select(Dependency)
        .options(
            selectinload(Dependency.source_workstream),
            selectinload(Dependency.target_workstream),
            selectinload(Dependency.gate),
        )
    )
    deps = dep_result.scalars().all()

    # D3 force graph format
    nodes = [
        {
            "id": w.id,
            "name": w.name,
            "short_name": w.short_name,
            "status": w.status.value if w.status else "not_started",
            "group": w.sort_order,
        }
        for w in workstreams
    ]

    links = [
        {
            "id": d.id,
            "source": d.source_workstream_id,
            "target": d.target_workstream_id,
            "description": d.description,
            "type": d.dep_type.value,
            "status": d.status.value,
            "criticality": d.criticality.value,
            "gate": d.gate.short_name if d.gate else None,
        }
        for d in deps
    ]

    return {"nodes": nodes, "links": links}


@router.get("/critical-path")
async def get_critical_path(db: AsyncSession = Depends(get_db)):
    """Compute critical path through dependency graph."""
    dep_result = await db.execute(
        select(Dependency)
        .where(Dependency.criticality.in_(["critical", "high"]))
        .options(
            selectinload(Dependency.source_workstream),
            selectinload(Dependency.target_workstream),
        )
    )
    critical_deps = dep_result.scalars().all()

    # Build adjacency for critical/high deps
    blocked_chains = []
    for d in critical_deps:
        if d.status.value in ("blocked", "at_risk"):
            blocked_chains.append({
                "dependency_id": d.id,
                "from": {"id": d.source_workstream.id, "name": d.source_workstream.name},
                "to": {"id": d.target_workstream.id, "name": d.target_workstream.name},
                "description": d.description,
                "status": d.status.value,
                "criticality": d.criticality.value,
            })

    return {
        "critical_dependencies": len([d for d in critical_deps if d.criticality.value == "critical"]),
        "high_dependencies": len([d for d in critical_deps if d.criticality.value == "high"]),
        "blocked_or_at_risk": blocked_chains,
    }
