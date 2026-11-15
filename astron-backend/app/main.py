from fastapi import FastAPI
from app.api.routes import observation, catalog
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Astron Backend API",
    description="Astronomical Observation Network API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
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
    return {
        "status": "healthy",
        "message": "The ASTRON backend is running smoothly.",
    }