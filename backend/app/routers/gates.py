from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.models import Gate, GateExitCriteria, Deliverable, Workstream

router = APIRouter()


@router.get("/")
async def list_gates(db: AsyncSession = Depends(get_db)):
    """All gates with exit criteria status."""
    result = await db.execute(
        select(Gate)
        .options(selectinload(Gate.exit_criteria))
        .order_by(Gate.sort_order)
    )
    gates = result.scalars().all()

    return [
        {
            "id": g.id,
            "name": g.name,
            "short_name": g.short_name,
            "description": g.description,
            "week_number": g.week_number,
            "due_date": str(g.due_date) if g.due_date else None,
            "status": g.status.value if g.status else None,
            "exit_criteria": [
                {"id": ec.id, "description": ec.description, "status": ec.status.value}
                for ec in sorted(g.exit_criteria, key=lambda x: x.sort_order)
            ],
            "criteria_complete": len([ec for ec in g.exit_criteria if ec.status.value == "complete"]),
            "criteria_total": len(g.exit_criteria),
        }
        for g in gates
    ]


@router.get("/timeline")
async def get_gate_timeline(db: AsyncSession = Depends(get_db)):
    """Gate timeline matrix: gates x workstreams with deliverable status."""
    gates_result = await db.execute(
        select(Gate)
        .options(selectinload(Gate.deliverables).selectinload(Deliverable.workstream))
        .order_by(Gate.sort_order)
    )
    gates = gates_result.scalars().all()

    ws_result = await db.execute(select(Workstream).order_by(Workstream.sort_order))
    workstreams = ws_result.scalars().all()

    matrix = []
    for ws in workstreams:
        row = {"workstream": {"id": ws.id, "name": ws.name, "short_name": ws.short_name}, "gates": {}}
        for g in gates:
            gate_deliverables = [d for d in g.deliverables if d.workstream_id == ws.id]
            if gate_deliverables:
                statuses = [d.status.value for d in gate_deliverables]
                if "blocked" in statuses:
                    cell_status = "blocked"
                elif "at_risk" in statuses:
                    cell_status = "at_risk"
                elif all(s == "complete" for s in statuses):
                    cell_status = "complete"
                elif any(s == "in_progress" for s in statuses):
                    cell_status = "in_progress"
                else:
                    cell_status = "not_started"
            else:
                cell_status = "not_started"

            row["gates"][g.short_name] = {
                "gate_id": g.id,
                "status": cell_status,
                "deliverable_count": len(gate_deliverables),
            }
        matrix.append(row)

    return {
        "gates": [{"id": g.id, "name": g.name, "short_name": g.short_name, "week": g.week_number} for g in gates],
        "matrix": matrix,
    }


@router.get("/{gate_id}")
async def get_gate(gate_id: int, db: AsyncSession = Depends(get_db)):
    """Gate detail with per-workstream deliverable status."""
    result = await db.execute(
        select(Gate)
        .where(Gate.id == gate_id)
        .options(
            selectinload(Gate.exit_criteria),
            selectinload(Gate.deliverables).selectinload(Deliverable.workstream),
        )
    )
    g = result.scalar_one_or_none()
    if not g:
        raise HTTPException(status_code=404, detail="Gate not found")

    # Group deliverables by workstream
    by_workstream = {}
    for d in g.deliverables:
        ws_id = d.workstream.id
        if ws_id not in by_workstream:
            by_workstream[ws_id] = {
                "workstream": {"id": d.workstream.id, "name": d.workstream.name},
                "deliverables": [],
            }
        by_workstream[ws_id]["deliverables"].append({
            "id": d.id,
            "name": d.name,
            "status": d.status.value,
        })

    return {
        "id": g.id,
        "name": g.name,
        "short_name": g.short_name,
        "description": g.description,
        "week_number": g.week_number,
        "status": g.status.value if g.status else None,
        "exit_criteria": [
            {"id": ec.id, "description": ec.description, "status": ec.status.value, "notes": ec.notes}
            for ec in sorted(g.exit_criteria, key=lambda x: x.sort_order)
        ],
        "workstream_deliverables": list(by_workstream.values()),
    }
