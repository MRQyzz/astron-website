import re

from app.core.config import FITS_DOWNLOAD_DIR
from app.providers.fits_inspector import inspect_fits_structure
from app.providers.wcs_wave import get_spectral_info
from app.providers.wcs_spatial import get_spatial_info

from app.providers.irsa import (
    search_observations as irsa_search_observations,
    parse_sia2_response,
    download_fits_product,
)


async def search_observations(
    ra: float,
    dec: float,
    radius: float,
) -> dict:
    """
    Handle SPHEREx observation search through IRSA SIA2.
    """

    votable_response = await irsa_search_observations(
        ra=ra,
        dec=dec,
        radius=radius,
    )

    observations = parse_sia2_response(votable_response)

    return {
        "service": "observations",
        "provider": "IRSA",
        "status": "success",
        "search_parameters": {
            "ra": ra,
            "dec": dec,
            "radius": radius,
        },
        "result_count": len(observations),
        "results": observations,
    }


async def download_observation_product(
    obs_id: str,
    access_url: str,
) -> dict:
    """
    Handle the download of a selected SPHEREx FITS product.
    """

    download_result = await download_fits_product(
        access_url=access_url,
        obs_id=obs_id,
    )

    return {
        "service": "observations",
        "provider": "IRSA",
        "status": "success",
        "product": {
            "obs_id": download_result["obs_id"],
            "filename": download_result["filename"],
            "size_bytes": download_result["size_bytes"],
            "status": download_result["status"],
        },
    }

async def inspect_observation_product(obs_id: str) -> dict:
    """
    Inspect a previously downloaded SPHEREx FITS product.
    """

    if not isinstance(obs_id, str) or not obs_id.strip():
        raise ValueError("obs_id must be a non-empty string")

    safe_obs_id = re.sub(r"[^A-Za-z0-9_.-]", "_", obs_id)

    matching_files = list(
        FITS_DOWNLOAD_DIR.glob(f"{safe_obs_id}_*.fits")
    )

    if not matching_files:
        raise FileNotFoundError(
            f"No downloaded FITS product found for {obs_id}"
        )

    if len(matching_files) > 1:
        raise ValueError(
            "Multiple FITS products found for this obs_id. "
            "A specific product identifier is required."
        )

    inspection_result = inspect_fits_structure(
        matching_files[0]
    )

    return {
        "service": "fits_inspection",
        "provider": "Astropy",
        "status": "success",
        "obs_id": obs_id,
        "file": {
            "filename": inspection_result["filename"],
            "size_bytes": inspection_result["size_bytes"],
        },
        "hdu_count": inspection_result["hdu_count"],
        "hdus": inspection_result["hdus"],
    }


async def get_observation_spectral_info(
    obs_id: str,
    x: float,
    y: float,
) -> dict:
    """
    Retrieve spectral information at a selected pixel
    from a previously downloaded SPHEREx FITS product.
    """

    if not isinstance(obs_id, str) or not obs_id.strip():
        raise ValueError("obs_id must be a non-empty string")

    safe_obs_id = re.sub(r"[^A-Za-z0-9_.-]", "_", obs_id)

    matching_files = list(
        FITS_DOWNLOAD_DIR.glob(f"{safe_obs_id}_*.fits")
    )

    if not matching_files:
        raise FileNotFoundError(
            f"No downloaded FITS product found for {obs_id}"
        )

    if len(matching_files) > 1:
        raise ValueError(
            "Multiple FITS products found for this obs_id. "
            "A specific product identifier is required."
        )

    spectral_result = get_spectral_info(
        file_path=matching_files[0],
        x=x,
        y=y,
    )

    return {
        "service": "observation_spectral_info",
        "provider": "IRSA",
        "status": "success",
        "obs_id": obs_id,
        **spectral_result,
    }


async def get_observation_pixel_info(
    obs_id: str,
    x: float,
    y: float,
) -> dict:
    """
    Retrieve spatial and spectral information
    at a selected pixel from a downloaded FITS product.
    """

    if not isinstance(obs_id, str) or not obs_id.strip():
        raise ValueError("obs_id must be a non-empty string")

    safe_obs_id = re.sub(r"[^A-Za-z0-9_.-]", "_", obs_id)

    matching_files = list(
        FITS_DOWNLOAD_DIR.glob(f"{safe_obs_id}_*.fits")
    )

    if not matching_files:
        raise FileNotFoundError(
            f"No downloaded FITS product found for {obs_id}"
        )

    if len(matching_files) > 1:
        raise ValueError(
            "Multiple FITS products found for this obs_id. "
            "A specific product identifier is required."
        )

    fits_path = matching_files[0]

    spatial_result = get_spatial_info(
        file_path=fits_path,
        x=x,
        y=y,
    )

    spectral_result = get_spectral_info(
        file_path=fits_path,
        x=x,
        y=y,
    )

    return {
        "service": "observation_pixel_info",
        "provider": "IRSA",
        "status": "success",
        "obs_id": obs_id,
        "pixel": {
            "x": float(x),
            "y": float(y),
        },
        "sky_coordinates": spatial_result["sky_coordinates"],
        "spectral_info": spectral_result["spectral_info"],
        "spatial_source": spatial_result["source"],
        "spectral_source": spectral_result["source"],
    }
