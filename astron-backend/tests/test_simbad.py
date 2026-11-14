
import pytest

from app.providers.simbad import build_adql_query


def test_build_adql_query():
    query = build_adql_query(
        ra=83.6331,
        dec=22.0145,
        radius=0.5,
        limit=100,
    )

    assert "SELECT TOP 100" in query
    assert "FROM basic" in query
    assert "main_id" in query
    assert "ra" in query
    assert "dec" in query
    assert "otype" in query
    assert "POINT('ICRS'" in query
    assert "CIRCLE('ICRS'" in query
    assert "83.6331" in query
    assert "22.0145" in query
    assert "0.5" in query


@pytest.mark.parametrize(
    "kwargs",
    [
        {"ra": -1, "dec": 22, "radius": 0.5},
        {"ra": 360, "dec": 22, "radius": 0.5},
        {"ra": 83, "dec": 91, "radius": 0.5},
        {"ra": 83, "dec": -91, "radius": 0.5},
        {"ra": 83, "dec": 22, "radius": 0},
        {"ra": 83, "dec": 22, "radius": 181},
        {"ra": float("nan"), "dec": 22, "radius": 0.5},
        {"ra": 83, "dec": 22, "radius": 0.5, "limit": 0},
    ],
)
def test_invalid_adql_parameters(kwargs):
    with pytest.raises(ValueError):
        build_adql_query(**kwargs)
