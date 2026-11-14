import math
import httpx
from app.core.config import SIMBAD_TAP_SYNC_URL, SIMBAD_TIMEOUT

def build_adql_query(
    ra: float,
    dec: float,
    radius: float,
    limit: int = 100,
) -> str:
    """
    Build an ADQL cone-search query for SIMBAD.

    Parameters
    ----------
    ra : float
        Right Ascension in degrees (0 <= RA < 360).
    dec : float
        Declination in degrees (-90 <= Dec <= 90).
    radius : float
        Search radius in degrees (0 < radius <= 180).
    limit : int
        Maximum number of returned objects.

    Returns
    -------
    str
        ADQL query string.
    """

    # Validate numeric inputs
    values = {
        "ra": ra,
        "dec": dec,
        "radius": radius,
    }

    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a numeric value")

        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")


    # Validate coordinate ranges
    if not 0 <= ra < 360:
        raise ValueError("RA must be between 0 and 360 degrees")

    if not -90 <= dec <= 90:
        raise ValueError("Dec must be between -90 and 90 degrees")

    if not 0 < radius <= 180:
        raise ValueError("Radius must be between 0 and 180 degrees")

    # Validate result limit
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise ValueError("Limit must be a positive integer")

    # Construct the ADQL query
    query = f"""
    SELECT TOP {limit}
        main_id,
        ra,
        dec,
        otype
    FROM basic
    WHERE CONTAINS(
        POINT('ICRS', ra, dec),
        CIRCLE('ICRS', {float(ra)!r}, {float(dec)!r}, {float(radius)!r})
    ) = 1
    """

    return query.strip()

async def search_objects(
    ra: float,
    dec: float,
    radius: float,
    limit: int = 100,
) -> dict:
    """
    Search astronomical objects using SIMBAD TAP API.

    Returns
    -------
    dict
        Raw JSON response from SIMBAD.
    """

    query = build_adql_query(
        ra=ra,
        dec=dec,
        radius=radius,
        limit=limit,
    )

    payload = {
        "REQUEST": "doQuery",
        "LANG": "ADQL",
        "FORMAT": "json",
        "QUERY": query,
    }

    timeout = httpx.Timeout(SIMBAD_TIMEOUT)

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
    ) as client:
        response = await client.post(
            SIMBAD_TAP_SYNC_URL,
            data=payload,
        )

        response.raise_for_status()

        try:
            return response.json()
        except ValueError as exc:
            raise RuntimeError(
                "SIMBAD returned a response that is not valid JSON"
            ) from exc