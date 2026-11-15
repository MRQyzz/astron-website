import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import observation, catalog

app = FastAPI(
    title="Astron Backend API",
    description="Astronomical Observation Network API",
    version="0.1.0",
)

# Include the default Vite development ports used by this project.
# CORS_ORIGINS can add extra origins without accidentally removing these defaults.
default_cors_origins = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
}
extra_cors_origins = {
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
}
cors_origins = sorted(default_cors_origins | extra_cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(observation.router)
app.include_router(catalog.router)


@app.get("/")
async def root():
    return {
        "application": "ASTRON",
        "description": "Astronomical Observation Network",
        "version": "0.1.0",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "The ASTRON backend is running smoothly."}
