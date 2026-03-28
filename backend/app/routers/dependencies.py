from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models import Dependency, Workstream
from app.models.dependency import DependencyType, DependencyStatus, Criticality
from app.models.person import Person
from app.auth.dependencies import get_current_user, require_owner_or_admin
from app.schemas.dependency import DependencyCreate, DependencyUpdate, DependencyResponse

router = APIRouter()


@router.get("/")
async def list_dependencies(
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(get_current_user),
):
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
async def get_critical_path(
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(get_current_user),
):
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


@router.post("/", response_model=DependencyResponse, status_code=201)
async def create_dependency(
    data: DependencyCreate,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(require_owner_or_admin),
):
    """Create a new cross-workstream dependency."""
    dep = Dependency(
        source_workstream_id=data.source_workstream_id,
        target_workstream_id=data.target_workstream_id,
        gate_id=data.gate_id,
        description=data.description,
        dep_type=DependencyType(data.dep_type),
        criticality=Criticality(data.criticality),
        notes=data.notes,
    )
    db.add(dep)
    await db.commit()
    await db.refresh(dep)
    return DependencyResponse(
        id=dep.id, source_workstream_id=dep.source_workstream_id,
        target_workstream_id=dep.target_workstream_id, gate_id=dep.gate_id,
        description=dep.description, dep_type=dep.dep_type.value,
        status=dep.status.value, criticality=dep.criticality.value,
        notes=dep.notes,
    )


@router.put("/{dependency_id}", response_model=DependencyResponse)
async def update_dependency(
    dependency_id: int,
    data: DependencyUpdate,
    db: AsyncSession = Depends(get_db),
    _user: Person = Depends(require_owner_or_admin),
):
    """Update dependency status or details."""
    result = await db.execute(select(Dependency).where(Dependency.id == dependency_id))
    dep = result.scalar_one_or_none()
    if not dep:
        raise HTTPException(status_code=404, detail="Dependency not found")

    updates = data.model_dump(exclude_unset=True)
    if "dep_type" in updates:
        updates["dep_type"] = DependencyType(updates["dep_type"])
    if "status" in updates:
        updates["status"] = DependencyStatus(updates["status"])
    if "criticality" in updates:
        updates["criticality"] = Criticality(updates["criticality"])
    for k, v in updates.items():
        setattr(dep, k, v)

    await db.commit()
    await db.refresh(dep)
    return DependencyResponse(
        id=dep.id, source_workstream_id=dep.source_workstream_id,
        target_workstream_id=dep.target_workstream_id, gate_id=dep.gate_id,
        description=dep.description, dep_type=dep.dep_type.value,
        status=dep.status.value, criticality=dep.criticality.value,
        notes=dep.notes,
    )
