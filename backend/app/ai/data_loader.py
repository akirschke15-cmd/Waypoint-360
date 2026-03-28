"""Load data from database into plain dicts for LLM context injection."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Workstream, Gate, GateExitCriteria, Dependency, Risk,
    Decision, Deliverable, StatusUpdate, ScopeChange,
)


async def load_all_workstreams(db: AsyncSession) -> dict:
    """Load all workstreams with scope, status, risks, deliverables."""
    result = await db.execute(
        select(Workstream)
        .options(
            selectinload(Workstream.owner),
            selectinload(Workstream.risks),
            selectinload(Workstream.deliverables),
            selectinload(Workstream.decisions),
        )
        .order_by(Workstream.sort_order)
    )
    workstreams = result.scalars().all()
    return {
        "workstreams": [
            {
                "id": w.id,
                "name": w.name,
                "short_name": w.short_name,
                "purpose": w.purpose,
                "scope_in": w.scope_in,
                "scope_out": w.scope_out,
                "baseline_scope": w.baseline_scope,
                "status": w.status.value if w.status else "unknown",
                "owner": w.owner.name if w.owner else "unassigned",
                "risks": [
                    {
                        "description": r.description,
                        "severity": r.severity.value,
                        "likelihood": r.likelihood.value,
                        "status": r.status.value,
                        "mitigation": r.mitigation,
                        "category": r.category,
                    }
                    for r in w.risks
                ],
                "deliverables_total": len(w.deliverables),
                "deliverables_complete": len([d for d in w.deliverables if d.status.value == "complete"]),
                "deliverables_at_risk": len([d for d in w.deliverables if d.status.value in ("at_risk", "blocked")]),
                "decisions_pending": len([d for d in w.decisions if d.status.value in ("needed", "pending")]),
            }
            for w in workstreams
        ]
    }


async def load_dependency_graph(db: AsyncSession) -> dict:
    """Load full dependency graph."""
    result = await db.execute(
        select(Dependency)
        .options(
            selectinload(Dependency.source_workstream),
            selectinload(Dependency.target_workstream),
            selectinload(Dependency.gate),
        )
    )
    deps = result.scalars().all()
    return {
        "dependencies": [
            {
                "from": d.source_workstream.name,
                "to": d.target_workstream.name,
                "description": d.description,
                "type": d.dep_type.value,
                "status": d.status.value,
                "criticality": d.criticality.value,
                "gate": d.gate.short_name if d.gate else None,
            }
            for d in deps
        ]
    }


async def load_gate_data(db: AsyncSession, gate_id: int | None = None) -> dict:
    """Load gate data with exit criteria and deliverable status."""
    query = select(Gate).options(
        selectinload(Gate.exit_criteria),
        selectinload(Gate.deliverables).selectinload(Deliverable.workstream),
    ).order_by(Gate.sort_order)

    if gate_id:
        query = query.where(Gate.id == gate_id)

    result = await db.execute(query)
    gates = result.scalars().all()

    return {
        "gates": [
            {
                "id": g.id,
                "name": g.name,
                "short_name": g.short_name,
                "week": g.week_number,
                "status": g.status.value if g.status else "not_started",
                "exit_criteria": [
                    {"description": ec.description, "status": ec.status.value}
                    for ec in sorted(g.exit_criteria, key=lambda x: x.sort_order)
                ],
                "deliverables": [
                    {
                        "workstream": d.workstream.name if d.workstream else "unknown",
                        "name": d.name,
                        "status": d.status.value,
                    }
                    for d in g.deliverables
                ],
            }
            for g in gates
        ]
    }


async def load_risks(db: AsyncSession) -> dict:
    """Load all open risks across workstreams."""
    result = await db.execute(
        select(Risk)
        .options(selectinload(Risk.workstream))
        .where(Risk.status.in_(["open", "accepted"]))
    )
    risks = result.scalars().all()
    return {
        "risks": [
            {
                "workstream": r.workstream.name if r.workstream else "unknown",
                "description": r.description,
                "severity": r.severity.value,
                "likelihood": r.likelihood.value,
                "mitigation": r.mitigation,
                "category": r.category,
                "status": r.status.value,
            }
            for r in risks
        ]
    }


async def load_scope_changes(db: AsyncSession) -> dict:
    """Load scope changes for creep detection."""
    result = await db.execute(
        select(ScopeChange).options(selectinload(ScopeChange.workstream))
    )
    changes = result.scalars().all()
    return {
        "scope_changes": [
            {
                "workstream": s.workstream.name if s.workstream else "unknown",
                "description": s.description,
                "change_type": s.change_type.value,
                "baseline_scope": s.baseline_scope,
                "current_scope": s.current_scope,
                "resolution": s.resolution,
            }
            for s in changes
        ]
    }


async def load_status_updates(db: AsyncSession, limit: int = 20) -> dict:
    """Load recent status updates."""
    result = await db.execute(
        select(StatusUpdate)
        .options(
            selectinload(StatusUpdate.workstream),
            selectinload(StatusUpdate.author),
        )
        .order_by(StatusUpdate.created_at.desc())
        .limit(limit)
    )
    updates = result.scalars().all()
    return {
        "status_updates": [
            {
                "workstream": u.workstream.name if u.workstream else "unknown",
                "author": u.author.name if u.author else "unknown",
                "content": u.content,
                "status_color": u.status_color.value,
                "created_at": str(u.created_at),
            }
            for u in updates
        ]
    }
