from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.database import init_db
from app.routers import workstreams, gates, dependencies, ai, auth, program


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(program.router, prefix=f"{settings.API_V1_PREFIX}/program", tags=["program"])
app.include_router(workstreams.router, prefix=f"{settings.API_V1_PREFIX}/workstreams", tags=["workstreams"])
app.include_router(gates.router, prefix=f"{settings.API_V1_PREFIX}/gates", tags=["gates"])
app.include_router(dependencies.router, prefix=f"{settings.API_V1_PREFIX}/dependencies", tags=["dependencies"])
app.include_router(ai.router, prefix=f"{settings.API_V1_PREFIX}/ai", tags=["ai"])


@app.get("/health")
async def health():
    return {"status": "healthy", "project": settings.PROJECT_NAME, "version": settings.VERSION}
