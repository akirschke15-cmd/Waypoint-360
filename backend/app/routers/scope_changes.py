from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timezone

from app.db.database import get_db
from app.models.scope_change import ScopeChange, ChangeType, FlaggedBy
from app.models.person import Person
from app.auth.dependencies import get_current_user, require_owner_or_admin
from app.schemas.scope_change import ScopeChangeCreate, ScopeChangeUpdate, ScopeChangeResponse

router = APIRouter()


@router.get("/", response_model=list[ScopeChangeResponse])
async def list_scope_changes(
    workstream_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(get_current_user),
):
    query = select(ScopeChange)
    if workstream_id:
        query = query.where(ScopeChange.workstream_id == workstream_id)
    result = await db.execute(query.order_by(ScopeChange.id.desc()))
    items = result.scalars().all()
    return [
        ScopeChangeResponse(
            id=s.id, workstream_id=s.workstream_id, description=s.description,
            change_type=s.change_type.value, baseline_scope=s.baseline_scope,
            current_scope=s.current_scope, flagged_by=s.flagged_by.value,
            flagged_at=s.flagged_at, resolution=s.resolution,
        )
        for s in items
    ]


@router.post("/", response_model=ScopeChangeResponse, status_code=201)
async def create_scope_change(
    data: ScopeChangeCreate,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(require_owner_or_admin),
):
    item = ScopeChange(
        workstream_id=data.workstream_id,
        description=data.description,
        change_type=ChangeType(data.change_type),
        baseline_scope=data.baseline_scope,
        current_scope=data.current_scope,
        flagged_by=FlaggedBy(data.flagged_by),
        flagged_at=datetime.now(timezone.utc),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return ScopeChangeResponse(
        id=item.id, workstream_id=item.workstream_id, description=item.description,
        change_type=item.change_type.value, baseline_scope=item.baseline_scope,
        current_scope=item.current_scope, flagged_by=item.flagged_by.value,
        flagged_at=item.flagged_at, resolution=item.resolution,
    )


@router.put("/{scope_change_id}", response_model=ScopeChangeResponse)
async def update_scope_change(
    scope_change_id: int,
    data: ScopeChangeUpdate,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(require_owner_or_admin),
):
    result = await db.execute(select(ScopeChange).where(ScopeChange.id == scope_change_id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Scope change not found")

    updates = data.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(s, k, v)

    await db.commit()
    await db.refresh(s)
    return ScopeChangeResponse(
        id=s.id, workstream_id=s.workstream_id, description=s.description,
        change_type=s.change_type.value, baseline_scope=s.baseline_scope,
        current_scope=s.current_scope, flagged_by=s.flagged_by.value,
        flagged_at=s.flagged_at, resolution=s.resolution,
    )
