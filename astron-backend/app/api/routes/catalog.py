from fastapi import APIRouter
from app.schemas.requests import SkySearchRequest
from app.services.catalog_services import search_catalog as catalog_search_service

router = APIRouter(
    prefix="/catalog",
    tags=["Catalog"]
)

@router.get("/")
async def catalog_status():
    return {
        "service": "catalog",
        "status": "available",
    }

@router.post("/search")
async def search_catalog(request: SkySearchRequest):
    # Here i would implement the logic to search the catalog based on the request parameters.
    # For demonstration purposes, we'll return the received parameters.
    return await catalog_search_service(
        ra=request.ra,
        dec=request.dec,
        radius=request.radius
    )