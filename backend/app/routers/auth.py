from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.person import Person, UserRole
from app.auth.security import verify_password, hash_password, create_access_token
from app.auth.dependencies import get_current_user, require_admin
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and return JWT token."""
    result = await db.execute(select(Person).where(Person.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role.value,
            title=user.title,
            organization=user.organization,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Person = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role.value,
        title=current_user.title,
        organization=current_user.organization,
    )


@router.post("/register", response_model=UserResponse)
async def register(
    name: str,
    email: str,
    password: str,
    role: str = "viewer",
    title: str | None = None,
    organization: str | None = None,
    db: AsyncSession = Depends(get_db),
    _admin: Person = Depends(require_admin),
):
    """Create a new user (admin only)."""
    existing = await db.execute(select(Person).where(Person.email == email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = Person(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        role=UserRole(role),
        title=title,
        organization=organization,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
        title=user.title,
        organization=user.organization,
    )
