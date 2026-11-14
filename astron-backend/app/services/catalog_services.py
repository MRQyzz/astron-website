
from app.providers.simbad import search_objects


async def search_catalog(
    ra: float,
    dec: float,
    radius: float,
) -> dict:
    """
    Search astronomical objects through the catalog service.

    Parameters
    ----------
    ra : float
        Right Ascension in degrees.
    dec : float
        Declination in degrees.
    radius : float
        Search radius in degrees.

    Returns
    -------
    dict
        Raw catalog response from SIMBAD.
    """

    result = await search_objects(
        ra=ra,
        dec=dec,
        radius=radius,
    )

    return result
