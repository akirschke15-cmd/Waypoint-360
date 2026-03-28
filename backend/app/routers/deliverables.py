from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.db.database import get_db
from app.models.deliverable import Deliverable, DeliverableStatus
from app.models.person import Person
from app.auth.dependencies import get_current_user, require_owner_or_admin
from app.schemas.deliverable import DeliverableCreate, DeliverableUpdate, DeliverableResponse

router = APIRouter()


@router.get("/", response_model=list[DeliverableResponse])
async def list_deliverables(
    workstream_id: Optional[int] = Query(None),
    gate_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(get_current_user),
):
    query = select(Deliverable)
    if workstream_id:
        query = query.where(Deliverable.workstream_id == workstream_id)
    if gate_id:
        query = query.where(Deliverable.gate_id == gate_id)
    if status:
        query = query.where(Deliverable.status == status)
    result = await db.execute(query.order_by(Deliverable.id))
    items = result.scalars().all()
    return [
        DeliverableResponse(
            id=d.id, workstream_id=d.workstream_id, gate_id=d.gate_id,
            name=d.name, description=d.description, status=d.status.value,
            due_date=d.due_date, assignee_id=d.assignee_id,
        )
        for d in items
    ]


@router.post("/", response_model=DeliverableResponse, status_code=201)
async def create_deliverable(
    data: DeliverableCreate,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(require_owner_or_admin),
):
    item = Deliverable(
        workstream_id=data.workstream_id,
        gate_id=data.gate_id,
        name=data.name,
        description=data.description,
        due_date=data.due_date,
        assignee_id=data.assignee_id,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return DeliverableResponse(
        id=item.id, workstream_id=item.workstream_id, gate_id=item.gate_id,
        name=item.name, description=item.description, status=item.status.value,
        due_date=item.due_date, assignee_id=item.assignee_id,
    )


@router.put("/{deliverable_id}", response_model=DeliverableResponse)
async def update_deliverable(
    deliverable_id: int,
    data: DeliverableUpdate,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(require_owner_or_admin),
):
    result = await db.execute(select(Deliverable).where(Deliverable.id == deliverable_id))
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    updates = data.model_dump(exclude_unset=True)
    if "status" in updates:
        updates["status"] = DeliverableStatus(updates["status"])
    for k, v in updates.items():
        setattr(d, k, v)

    await db.commit()
    await db.refresh(d)
    return DeliverableResponse(
        id=d.id, workstream_id=d.workstream_id, gate_id=d.gate_id,
        name=d.name, description=d.description, status=d.status.value,
        due_date=d.due_date, assignee_id=d.assignee_id,
    )


@router.delete("/{deliverable_id}")
async def delete_deliverable(
    deliverable_id: int,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(require_owner_or_admin),
):
    result = await db.execute(select(Deliverable).where(Deliverable.id == deliverable_id))
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    await db.delete(d)
    await db.commit()
    return {"status": "deleted", "id": deliverable_id}
