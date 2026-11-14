import asyncio
from unittest.mock import AsyncMock, patch
import pytest
from app.services.catalog_services import search_catalog

# TEST 1: SIMBAD returns astronomical objects
def test_search_catalog_returns_data():
    mock_response = {
        "metadata": [
            {"name": "main_id"},
            {"name": "ra"},
            {"name": "dec"},
            {"name": "otype"},
        ],
        "data": [
            ["HD 245198", 83.9502, 22.0832, "*"],
            ["HD 245010", 83.7273, 21.9458, "V*"],
        ],
    }

    async def run_test():
        with patch(
            "app.services.catalog_services.search_objects",
            new_callable=AsyncMock,
        ) as mock_search:
            mock_search.return_value = mock_response

            result = await search_catalog(
                ra=83.6331,
                dec=22.0145,
                radius=0.5,
            )

            assert result == mock_response

            mock_search.assert_awaited_once_with(
                ra=83.6331,
                dec=22.0145,
                radius=0.5,
            )

    asyncio.run(run_test())

# TEST 2: SIMBAD returns an empty result
def test_search_catalog_returns_empty_data():
    mock_response = {
        "metadata": [],
        "data": [],
    }

    async def run_test():
        with patch(
            "app.services.catalog_services.search_objects",
            new_callable=AsyncMock, 
        ) as mock_search:
            mock_search.return_value = mock_response
            result = await search_catalog(
                ra=83.6331,
                dec=22.0145,
                radius=0.5,
            )
            assert result == mock_response
            assert result["data"] == []

    asyncio.run(run_test())

# TEST 3: SIMBAD raises an exception
def test_search_catalog_propragates_provide_error():

    async def run_test():
        with patch(
            "app.services.catalog_services.search_objects",
            new_callable=AsyncMock,
        ) as mock_search:
            mock_search.side_effect = RuntimeError(
                "SIMBAD connection failed"
            )

            with pytest.raises(
                RuntimeError,
                match="SIMBAD connection failed",
            ):
                await search_catalog(
                    ra=83.6331,
                    dec=22.0145,
                    radius=0.5,
                )

    asyncio.run(run_test())