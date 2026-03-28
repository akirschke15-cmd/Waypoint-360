from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.db.database import get_db
from app.models.status_update import StatusUpdate, StatusColor
from app.models.person import Person
from app.auth.dependencies import get_current_user, require_owner_or_admin
from app.schemas.status_update import StatusUpdateCreate, StatusUpdateResponse

router = APIRouter()


@router.get("/", response_model=list[StatusUpdateResponse])
async def list_status_updates(
    workstream_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(get_current_user),
):
    query = select(StatusUpdate)
    if workstream_id:
        query = query.where(StatusUpdate.workstream_id == workstream_id)
    result = await db.execute(query.order_by(StatusUpdate.created_at.desc()))
    items = result.scalars().all()
    return [
        StatusUpdateResponse(
            id=s.id, workstream_id=s.workstream_id, gate_id=s.gate_id,
            author_id=s.author_id, content=s.content,
            status_color=s.status_color.value, created_at=s.created_at,
        )
        for s in items
    ]


@router.post("/", response_model=StatusUpdateResponse, status_code=201)
async def create_status_update(
    data: StatusUpdateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Person = Depends(require_owner_or_admin),
):
    item = StatusUpdate(
        workstream_id=data.workstream_id,
        gate_id=data.gate_id,
        author_id=current_user.id,
        content=data.content,
        status_color=StatusColor(data.status_color),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return StatusUpdateResponse(
        id=item.id, workstream_id=item.workstream_id, gate_id=item.gate_id,
        author_id=item.author_id, content=item.content,
        status_color=item.status_color.value, created_at=item.created_at,
    )
