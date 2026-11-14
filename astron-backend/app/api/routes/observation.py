from fastapi import APIRouter
from app.schemas.requests import SkySearchRequest
from app.services.observation_services import search_observations as observation_search_service

router = APIRouter(
    prefix="/obervation",
    tags=["Observation"]
)

@router.get("/")
async def observation_status():
    return {
        "service": "observation",
        "status": "available",
    }

@router.post("/search")
async def search_observations(request: SkySearchRequest):
    return await observation_search_service(
        ra=request.ra,
        dec=request.dec,
        radius=request.radius
    )
