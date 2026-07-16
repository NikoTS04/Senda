from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.config import settings

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
