from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.models import Workstream, Deliverable, Risk, Decision, Dependency, StatusUpdate

router = APIRouter()


@router.get("/")
async def list_workstreams(db: AsyncSession = Depends(get_db)):
    """List all workstreams with summary status."""
    result = await db.execute(
        select(Workstream)
        .options(
            selectinload(Workstream.owner),
            selectinload(Workstream.risks),
            selectinload(Workstream.deliverables),
        )
        .order_by(Workstream.sort_order)
    )
    workstreams = result.scalars().all()

    return [
        {
            "id": w.id,
            "name": w.name,
            "short_name": w.short_name,
            "purpose": w.purpose,
            "status": w.status.value if w.status else None,
            "owner": {"id": w.owner.id, "name": w.owner.name} if w.owner else None,
            "risk_count": len([r for r in w.risks if r.status.value == "open"]),
            "deliverable_count": len(w.deliverables),
            "deliverables_complete": len([d for d in w.deliverables if d.status.value == "complete"]),
        }
        for w in workstreams
    ]


@router.get("/{workstream_id}")
async def get_workstream(workstream_id: int, db: AsyncSession = Depends(get_db)):
    """Full workstream detail with all related data."""
    result = await db.execute(
        select(Workstream)
        .where(Workstream.id == workstream_id)
        .options(
            selectinload(Workstream.owner),
            selectinload(Workstream.members),
            selectinload(Workstream.deliverables).selectinload(Deliverable.gate),
            selectinload(Workstream.risks),
            selectinload(Workstream.decisions),
            selectinload(Workstream.status_updates),
            selectinload(Workstream.scope_changes),
            selectinload(Workstream.outbound_dependencies).selectinload(Dependency.target_workstream),
            selectinload(Workstream.inbound_dependencies).selectinload(Dependency.source_workstream),
        )
    )
    w = result.scalar_one_or_none()
    if not w:
        raise HTTPException(status_code=404, detail="Workstream not found")

    return {
        "id": w.id,
        "name": w.name,
        "short_name": w.short_name,
        "purpose": w.purpose,
        "scope_in": w.scope_in,
        "scope_out": w.scope_out,
        "baseline_scope": w.baseline_scope,
        "status": w.status.value if w.status else None,
        "owner": {"id": w.owner.id, "name": w.owner.name, "title": w.owner.title} if w.owner else None,
        "members": [{"id": m.id, "name": m.name, "title": m.title, "capacity_pct": m.capacity_pct} for m in w.members],
        "deliverables": [
            {
                "id": d.id,
                "name": d.name,
                "description": d.description,
                "status": d.status.value,
                "gate": {"id": d.gate.id, "name": d.gate.name, "short_name": d.gate.short_name} if d.gate else None,
            }
            for d in w.deliverables
        ],
        "risks": [
            {
                "id": r.id,
                "description": r.description,
                "severity": r.severity.value,
                "likelihood": r.likelihood.value,
                "mitigation": r.mitigation,
                "status": r.status.value,
            }
            for r in w.risks
        ],
        "decisions": [
            {
                "id": d.id,
                "description": d.description,
                "status": d.status.value,
                "decision_maker": d.decision_maker,
                "due_date": str(d.due_date) if d.due_date else None,
            }
            for d in w.decisions
        ],
        "needs_from": [
            {
                "id": dep.id,
                "workstream": {"id": dep.target_workstream.id, "name": dep.target_workstream.name},
                "description": dep.description,
                "status": dep.status.value,
                "criticality": dep.criticality.value,
            }
            for dep in w.outbound_dependencies
        ],
        "provides_to": [
            {
                "id": dep.id,
                "workstream": {"id": dep.source_workstream.id, "name": dep.source_workstream.name},
                "description": dep.description,
                "status": dep.status.value,
                "criticality": dep.criticality.value,
            }
            for dep in w.inbound_dependencies
        ],
        "status_updates": [
            {
                "id": su.id,
                "content": su.content,
                "status_color": su.status_color.value,
                "created_at": str(su.created_at),
            }
            for su in sorted(w.status_updates, key=lambda x: x.created_at, reverse=True)[:10]
        ],
    }


@router.put("/{workstream_id}")
async def update_workstream(workstream_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    """Update workstream fields."""
    result = await db.execute(select(Workstream).where(Workstream.id == workstream_id))
    w = result.scalar_one_or_none()
    if not w:
        raise HTTPException(status_code=404, detail="Workstream not found")

    updatable = ["name", "purpose", "scope_in", "scope_out", "status"]
    for field in updatable:
        if field in data:
            setattr(w, field, data[field])

    await db.commit()
    return {"status": "updated", "id": workstream_id}
