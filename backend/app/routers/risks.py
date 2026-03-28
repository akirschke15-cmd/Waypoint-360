from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.db.database import get_db
from app.models.risk import Risk, Severity, Likelihood, RiskStatus
from app.models.person import Person
from app.auth.dependencies import get_current_user, require_owner_or_admin
from app.schemas.risk import RiskCreate, RiskUpdate, RiskResponse

router = APIRouter()


@router.get("/", response_model=list[RiskResponse])
async def list_risks(
    workstream_id: Optional[int] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(get_current_user),
):
    """List risks, optionally filtered by workstream, severity, or status."""
    query = select(Risk)
    if workstream_id:
        query = query.where(Risk.workstream_id == workstream_id)
    if severity:
        query = query.where(Risk.severity == severity)
    if status:
        query = query.where(Risk.status == status)
    result = await db.execute(query.order_by(Risk.id))
    risks = result.scalars().all()
    return [
        RiskResponse(
            id=r.id, workstream_id=r.workstream_id, description=r.description,
            severity=r.severity.value, likelihood=r.likelihood.value,
            impact=r.impact, mitigation=r.mitigation,
            status=r.status.value, owner_id=r.owner_id, category=r.category,
        )
        for r in risks
    ]


@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(
    risk_id: int,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(get_current_user),
):
    result = await db.execute(select(Risk).where(Risk.id == risk_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Risk not found")
    return RiskResponse(
        id=r.id, workstream_id=r.workstream_id, description=r.description,
        severity=r.severity.value, likelihood=r.likelihood.value,
        impact=r.impact, mitigation=r.mitigation,
        status=r.status.value, owner_id=r.owner_id, category=r.category,
    )


@router.post("/", response_model=RiskResponse, status_code=201)
async def create_risk(
    data: RiskCreate,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(require_owner_or_admin),
):
    risk = Risk(
        workstream_id=data.workstream_id,
        description=data.description,
        severity=Severity(data.severity),
        likelihood=Likelihood(data.likelihood),
        impact=data.impact,
        mitigation=data.mitigation,
        owner_id=data.owner_id,
        category=data.category,
    )
    db.add(risk)
    await db.commit()
    await db.refresh(risk)
    return RiskResponse(
        id=risk.id, workstream_id=risk.workstream_id, description=risk.description,
        severity=risk.severity.value, likelihood=risk.likelihood.value,
        impact=risk.impact, mitigation=risk.mitigation,
        status=risk.status.value, owner_id=risk.owner_id, category=risk.category,
    )


@router.put("/{risk_id}", response_model=RiskResponse)
async def update_risk(
    risk_id: int,
    data: RiskUpdate,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(require_owner_or_admin),
):
    result = await db.execute(select(Risk).where(Risk.id == risk_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Risk not found")

    updates = data.model_dump(exclude_unset=True)
    if "severity" in updates:
        updates["severity"] = Severity(updates["severity"])
    if "likelihood" in updates:
        updates["likelihood"] = Likelihood(updates["likelihood"])
    if "status" in updates:
        updates["status"] = RiskStatus(updates["status"])
    for k, v in updates.items():
        setattr(r, k, v)

    await db.commit()
    await db.refresh(r)
    return RiskResponse(
        id=r.id, workstream_id=r.workstream_id, description=r.description,
        severity=r.severity.value, likelihood=r.likelihood.value,
        impact=r.impact, mitigation=r.mitigation,
        status=r.status.value, owner_id=r.owner_id, category=r.category,
    )


@router.delete("/{risk_id}")
async def delete_risk(
    risk_id: int,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(require_owner_or_admin),
):
    result = await db.execute(select(Risk).where(Risk.id == risk_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Risk not found")
    await db.delete(r)
    await db.commit()
    return {"status": "deleted", "id": risk_id}
