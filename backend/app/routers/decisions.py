from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.db.database import get_db
from app.models.decision import Decision, DecisionStatus
from app.models.person import Person
from app.auth.dependencies import get_current_user, require_owner_or_admin
from app.schemas.decision import DecisionCreate, DecisionUpdate, DecisionResponse

router = APIRouter()


@router.get("/", response_model=list[DecisionResponse])
async def list_decisions(
    workstream_id: Optional[int] = Query(None),
    gate_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(get_current_user),
):
    query = select(Decision)
    if workstream_id:
        query = query.where(Decision.workstream_id == workstream_id)
    if gate_id:
        query = query.where(Decision.gate_id == gate_id)
    if status:
        query = query.where(Decision.status == status)
    result = await db.execute(query.order_by(Decision.id))
    decisions = result.scalars().all()
    return [
        DecisionResponse(
            id=d.id, workstream_id=d.workstream_id, gate_id=d.gate_id,
            description=d.description, status=d.status.value,
            decision_maker=d.decision_maker, due_date=d.due_date,
            resolution=d.resolution, decided_at=d.decided_at, impact=d.impact,
        )
        for d in decisions
    ]


@router.post("/", response_model=DecisionResponse, status_code=201)
async def create_decision(
    data: DecisionCreate,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(require_owner_or_admin),
):
    dec = Decision(
        workstream_id=data.workstream_id,
        gate_id=data.gate_id,
        description=data.description,
        decision_maker=data.decision_maker,
        due_date=data.due_date,
        impact=data.impact,
    )
    db.add(dec)
    await db.commit()
    await db.refresh(dec)
    return DecisionResponse(
        id=dec.id, workstream_id=dec.workstream_id, gate_id=dec.gate_id,
        description=dec.description, status=dec.status.value,
        decision_maker=dec.decision_maker, due_date=dec.due_date,
        resolution=dec.resolution, decided_at=dec.decided_at, impact=dec.impact,
    )


@router.put("/{decision_id}", response_model=DecisionResponse)
async def update_decision(
    decision_id: int,
    data: DecisionUpdate,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(require_owner_or_admin),
):
    result = await db.execute(select(Decision).where(Decision.id == decision_id))
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")

    updates = data.model_dump(exclude_unset=True)
    if "status" in updates:
        updates["status"] = DecisionStatus(updates["status"])
    for k, v in updates.items():
        setattr(d, k, v)

    await db.commit()
    await db.refresh(d)
    return DecisionResponse(
        id=d.id, workstream_id=d.workstream_id, gate_id=d.gate_id,
        description=d.description, status=d.status.value,
        decision_maker=d.decision_maker, due_date=d.due_date,
        resolution=d.resolution, decided_at=d.decided_at, impact=d.impact,
    )


@router.delete("/{decision_id}")
async def delete_decision(
    decision_id: int,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(require_owner_or_admin),
):
    result = await db.execute(select(Decision).where(Decision.id == decision_id))
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="Decision not found")
    await db.delete(d)
    await db.commit()
    return {"status": "deleted", "id": decision_id}
