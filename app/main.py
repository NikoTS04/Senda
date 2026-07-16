from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.config import settings
from app.infrastructure.database.session import Base, engine
from app.infrastructure.database.models import EscritoDB, UsuarioDB, ComentarioDB  # Import models to register metadata
from app.infrastructure.api.routers import writings, auth, comments

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Senda API",
    description="API para la plataforma Senda de escritos y feedback",
    version="1.0.0"
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": settings.ENV}

# Include API routers
app.include_router(writings.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(comments.router, prefix="/api/v1")
