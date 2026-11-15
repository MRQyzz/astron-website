import re
from pathlib import Path

from astropy.io import fits

from app.core.config import FITS_DOWNLOAD_DIR, FITS_MAX_SIZE
from app.providers.fits_inspector import inspect_fits_structure
from app.providers.wcs_wave import get_spectral_info
from app.providers.wcs_spatial import get_spatial_info
from app.providers.irsa import (
    search_observations as irsa_search_observations,
    parse_sia2_response,
    download_fits_product,
)


def _find_product(obs_id: str) -> Path:
    if not isinstance(obs_id, str) or not obs_id.strip():
        raise ValueError("obs_id must be a non-empty string")
    safe_obs_id = re.sub(r"[^A-Za-z0-9_.-]", "_", obs_id)
    matches = sorted(FITS_DOWNLOAD_DIR.glob(f"{safe_obs_id}_*.fits"))
    if not matches:
        raise FileNotFoundError(
            f"No FITS product found for {obs_id}. Download a product or upload a local FITS file first."
        )
    if len(matches) > 1:
        raise ValueError(
            "Multiple FITS products found for this obs_id. Use a unique observation ID for each local file."
        )
    return matches[0]


async def search_observations(ra: float, dec: float, radius: float) -> dict:
    votable_response = await irsa_search_observations(ra=ra, dec=dec, radius=radius)
    observations = parse_sia2_response(votable_response)
    return {
        "service": "observations",
        "provider": "IRSA",
        "status": "success",
        "search_parameters": {"ra": ra, "dec": dec, "radius": radius},
        "result_count": len(observations),
        "results": observations,
    }


async def download_observation_product(obs_id: str, access_url: str) -> dict:
    result = await download_fits_product(access_url=access_url, obs_id=obs_id)
    return {
        "service": "observations",
        "provider": "IRSA",
        "status": "success",
        "product": {
            "obs_id": result["obs_id"],
            "filename": result["filename"],
            "size_bytes": result["size_bytes"],
            "status": result["status"],
        },
    }


async def save_uploaded_fits(obs_id: str, content: bytes, filename: str) -> dict:
    if not isinstance(obs_id, str) or not obs_id.strip():
        raise ValueError("obs_id must be a non-empty string")
    if not content:
        raise ValueError("Uploaded FITS file is empty")
    if len(content) > FITS_MAX_SIZE:
        raise ValueError("FITS product exceeds maximum size")
    if not filename.lower().endswith((".fits", ".fit", ".fts")):
        raise ValueError("Please upload a FITS file (.fits, .fit, or .fts)")

    safe_obs_id = re.sub(r"[^A-Za-z0-9_.-]", "_", obs_id.strip())
    FITS_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination = FITS_DOWNLOAD_DIR / f"{safe_obs_id}_local.fits"

    temporary = destination.with_suffix(".fits.part")
    try:
        temporary.write_bytes(content)
        with fits.open(temporary, mode="readonly", memmap=False) as hdul:
            hdul.verify("exception")
            if len(hdul) == 0:
                raise ValueError("FITS file contains no HDUs")
        temporary.replace(destination)
    except Exception as exc:
        temporary.unlink(missing_ok=True)
        if isinstance(exc, ValueError):
            raise
        raise ValueError("Uploaded file is not a valid FITS file") from exc

    return {
        "service": "fits_upload",
        "provider": "Local",
        "status": "success",
        "obs_id": obs_id,
        "filename": destination.name,
        "size_bytes": destination.stat().st_size,
    }


async def inspect_observation_product(obs_id: str) -> dict:
    path = _find_product(obs_id)
    result = inspect_fits_structure(path)
    return {
        "service": "fits_inspection",
        "provider": "Astropy",
        "status": "success",
        "obs_id": obs_id,
        "file": {"filename": result["filename"], "size_bytes": result["size_bytes"]},
        "hdu_count": result["hdu_count"],
        "hdus": result["hdus"],
    }


async def get_observation_spectral_info(obs_id: str, x: float, y: float) -> dict:
    result = get_spectral_info(file_path=_find_product(obs_id), x=x, y=y)
    return {
        "service": "observation_spectral_info",
        "provider": "Astropy WCS-WAVE",
        "status": "success",
        "obs_id": obs_id,
        **result,
    }


async def get_observation_pixel_info(obs_id: str, x: float, y: float) -> dict:
    path = _find_product(obs_id)
    spatial = get_spatial_info(file_path=path, x=x, y=y)
    spectral = get_spectral_info(file_path=path, x=x, y=y)
    return {
        "service": "observation_pixel_info",
        "provider": "Astropy",
        "status": "success",
        "obs_id": obs_id,
        "pixel": {"x": float(x), "y": float(y)},
        "sky_coordinates": spatial["sky_coordinates"],
        "spectral_info": spectral["spectral_info"],
        "spatial_source": spatial["source"],
        "spectral_source": spectral["source"],
    }
