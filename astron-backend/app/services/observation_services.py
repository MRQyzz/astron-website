
async def search_observations(ra: float, dec: float, radius: float):
    """
    Handle SPHEREx observation search.
    IRSA integration will be implemented later.
    """

    return {
        "service": "observations",
        "status": "request_received",
        "search_parameters": {
            "ra": ra,
            "dec": dec,
            "radius": radius,
        },
        "results": [],
    }
