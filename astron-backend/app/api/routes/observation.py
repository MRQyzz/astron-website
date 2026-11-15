import httpx
from fastapi import APIRouter, HTTPException

from app.schemas.requests import (
    SkySearchRequest,
    FitsDownloadRequest,
    FitsInspectRequest,
    SpectralInfoRequest,
    PixelInfoRequest,
)

from app.services.observation_services import (
    search_observations as observation_search_service,
    download_observation_product as observation_download_service,
    inspect_observation_product as observation_inspection_service,
    get_observation_spectral_info as spectral_info_service,
    get_observation_pixel_info as pixel_info_service,
)

router = APIRouter(prefix="/observations", tags=["Observation"])


@router.get("/")
async def observation_status():
    return {"service": "observation", "status": "available"}


@router.post("/search")
async def search_observations(request: SkySearchRequest):
    try:
        return await observation_search_service(
            ra=request.ra, dec=request.dec, radius=request.radius
        )
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="IRSA did not respond within the allowed time. Try again later.",
        ) from exc
    except httpx.NetworkError as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to establish a connection to IRSA.",
        ) from exc
    except httpx.HTTPStatusError as exc:
        upstream_status = exc.response.status_code
        if upstream_status == 429:
            status_code = 503
            detail = "IRSA is rate-limiting requests. Try again later."
        elif 500 <= upstream_status <= 599:
            status_code = 502
            detail = f"IRSA upstream service returned HTTP {upstream_status}."
        else:
            status_code = 502
            detail = "IRSA rejected the observation search request."
        raise HTTPException(status_code=status_code, detail=detail) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail="IRSA returned an unreadable observation response.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/download")
async def download_observation(request: FitsDownloadRequest):
    try:
        return await observation_download_service(
            obs_id=request.obs_id, access_url=request.access_url
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve the selected FITS product from IRSA.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/inspect")
async def inspect_observation(request: FitsInspectRequest):
    try:
        return await observation_inspection_service(obs_id=request.obs_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/spectral-info")
async def get_spectral_info(request: SpectralInfoRequest):
    try:
        return await spectral_info_service(
            obs_id=request.obs_id, x=request.x, y=request.y
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/pixel-info")
async def get_pixel_info(request: PixelInfoRequest):
    try:
        return await pixel_info_service(
            obs_id=request.obs_id, x=request.x, y=request.y
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
