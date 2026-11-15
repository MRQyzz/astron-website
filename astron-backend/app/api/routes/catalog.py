import httpx
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
    return await catalog_search_service(
        ra=request.ra,
        dec=request.dec,
        radius=request.radius,
    )


@router.get("/search-by-name")
async def search_catalog_by_name(
    name: str = Query(..., min_length=1, max_length=128),
):
    try:
        return await search_objects_by_name(name=name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except httpx.HTTPStatusError as exc:
        # Preserve a short upstream diagnostic instead of returning an opaque 500.
        upstream_detail = exc.response.text.strip()
        if len(upstream_detail) > 500:
            upstream_detail = upstream_detail[:500] + "..."
        detail = (
            f"SIMBAD TAP returned HTTP {exc.response.status_code}."
            if not upstream_detail
            else f"SIMBAD TAP returned HTTP {exc.response.status_code}: {upstream_detail}"
        )
        raise HTTPException(status_code=502, detail=detail) from exc
    except (httpx.TimeoutException, httpx.NetworkError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to reach the SIMBAD TAP service.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
