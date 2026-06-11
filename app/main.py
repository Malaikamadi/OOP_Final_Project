from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base

# Import all models so Alembic and Base.metadata.create_all can discover them
from app.models import user, clinic, service, doctor, appointment, review, opening_hours  # noqa: F401

from app.routes import auth, clinics, services, doctors, appointments, reviews, opening_hours as oh_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (for dev; use Alembic in production)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A REST API for searching and managing local clinic services. "
        "Features include clinic registration, GPS-based search, doctor profiles, "
        "appointment booking, ratings/reviews, and JWT authentication."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(auth.router, prefix=PREFIX + "/auth", tags=["Authentication"])
app.include_router(clinics.router, prefix=PREFIX + "/clinics", tags=["Clinics"])
app.include_router(services.router, prefix=PREFIX, tags=["Services"])
app.include_router(doctors.router, prefix=PREFIX, tags=["Doctors"])
app.include_router(appointments.router, prefix=PREFIX + "/appointments", tags=["Appointments"])
app.include_router(reviews.router, prefix=PREFIX, tags=["Reviews"])
app.include_router(oh_router.router, prefix=PREFIX, tags=["Opening Hours"])


@app.get("/", tags=["Health"])
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
