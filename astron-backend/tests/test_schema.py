import pytest
from pydantic import ValidationError
from app.schemas.requests import SkySearchRequest

def test_valid_sky_coordinates():
    request = SkySearchRequest(
        ra=83.6331,
        dec=22.0145,
        radius=0.5,
    )

    assert request.ra == 83.6331
    assert request.dec == 22.0145
    assert request.radius == 0.5

@pytest.mark.parametrize(
    "data",
    [
        {"ra": -1, "dec": 22, "radius": 0.5},
        {"ra": 360, "dec": 22, "radius": 0.5},
        {"ra": 83, "dec": 91, "radius": 0.5},
        {"ra": 83, "dec": -91, "radius": 0.5},
        {"ra": 83, "dec": 22, "radius": 0},
        {"ra": 83, "dec": 22, "radius": 181},
    ],
)

def test_invalid_sky_coordinates(data):
    with pytest.raises(ValidationError):
        SkySearchRequest(**data)