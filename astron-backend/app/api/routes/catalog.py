from fastapi import APIRouter, HTTPException, Query
from app.schemas.requests import SkySearchRequest
from app.services.catalog_services import search_catalog as catalog_search_service
from app.providers.simbad import search_objects_by_name

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

@router.get("/search-by-name")
async def search_catalog_by_name(
    name: str = Query(..., min_length=1, max_length=128),
):
    try:
        return await search_objects_by_name(name=name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
