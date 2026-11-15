import pytest
from pathlib import Path
import httpx
from app.providers.irsa import build_sia2_params
from app.providers.irsa import parse_sia2_response
from app.providers.irsa import download_fits_product

def test_build_sia2_params_success():
    params = build_sia2_params(
        ra=83.6331,
        dec=22.0145,
        radius=0.1,
        maxrec=1,
    )

    assert params == {
        "COLLECTION": "spherex_dr1",
        "POS": "circle 83.6331 22.0145 0.1",
        "MAXREC": 1,
    }


@pytest.mark.parametrize(
    "ra, dec, radius",
    [
        (400, 22, 0.1),
        (-1, 22, 0.1),
        (83, 100, 0.1),
        (83, -100, 0.1),
        (83, 22, 0),
        (83, 22, 181),
    ],
)
def test_build_sia2_params_invalid_coordinates(
    ra, dec, radius
):
    with pytest.raises(ValueError):
        build_sia2_params(ra, dec, radius)


@pytest.mark.parametrize(
    "maxrec",
    [0, -1, 1.5, True],
)
def test_build_sia2_params_invalid_maxrec(maxrec):
    with pytest.raises(ValueError):
        build_sia2_params(
            ra=83,
            dec=22,
            radius=0.1,
            maxrec=maxrec,
        )


def test_build_sia2_params_invalid_collection():
    with pytest.raises(ValueError):
        build_sia2_params(
            ra=83,
            dec=22,
            radius=0.1,
            collection="",
        )


SAMPLE_VOTABLE = """<?xml version="1.0"?>
<VOTABLE version="1.3"
 xmlns="http://www.ivoa.net/xml/VOTable/v1.3">
    <RESOURCE type="results">
        <TABLE>
            <FIELD name="obs_id" datatype="char" arraysize="*"/>
            <FIELD name="s_ra" datatype="double"/>
            <FIELD name="s_dec" datatype="double"/>
            <FIELD name="access_format" datatype="char" arraysize="*"/>
            <DATA>
                <TABLEDATA>
                    <TR>
                        <TD>TEST_OBS_001</TD>
                        <TD>83.35</TD>
                        <TD>21.68</TD>
                        <TD>image/fits</TD>
                    </TR>
                </TABLEDATA>
            </DATA>
        </TABLE>
    </RESOURCE>
</VOTABLE>
"""


EMPTY_VOTABLE = """<?xml version="1.0"?>
<VOTABLE version="1.3"
 xmlns="http://www.ivoa.net/xml/VOTable/v1.3">
    <RESOURCE type="results">
        <TABLE>
            <FIELD name="obs_id" datatype="char" arraysize="*"/>
            <FIELD name="s_ra" datatype="double"/>
            <DATA>
                <TABLEDATA/>
            </DATA>
        </TABLE>
    </RESOURCE>
</VOTABLE>
"""


def test_parse_valid_votable():
    records = parse_sia2_response(SAMPLE_VOTABLE)

    assert len(records) == 1
    assert records[0]["obs_id"] == "TEST_OBS_001"
    assert records[0]["s_ra"] == 83.35
    assert records[0]["s_dec"] == 21.68
    assert records[0]["access_format"] == "image/fits"


def test_parse_empty_votable():
    records = parse_sia2_response(EMPTY_VOTABLE)

    assert records == []


@pytest.mark.parametrize(
    "invalid_input",
    [
        "",
        "   ",
        "<INVALID_XML>",
    ],
)
def test_parse_invalid_votable(invalid_input):
    with pytest.raises(ValueError):
        parse_sia2_response(invalid_input)



class MockFITSResponse:
    status_code = 200
    headers = {
        "content-type": "application/fits",
        "content-length": "2880",
    }
    url = httpx.URL("https://irsa.ipac.caltech.edu/test.fits")

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    def raise_for_status(self):
        pass

    async def aiter_bytes(self, chunk_size=1024 * 1024):
        yield b"SIMPLE  =" + b" " * 2871


class MockFITSClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    def stream(self, method, url):
        return MockFITSResponse()


def test_download_fits_rejects_untrusted_url():
    import asyncio

    with pytest.raises(ValueError, match="Untrusted"):
        asyncio.run(
            download_fits_product(
                "https://example.com/test.fits",
                "TEST_001",
            )
        )


def test_download_fits_success(monkeypatch, tmp_path):
    import asyncio
    import app.providers.irsa as irsa

    monkeypatch.setattr(
        irsa,
        "FITS_DOWNLOAD_DIR",
        tmp_path,
    )

    monkeypatch.setattr(
        irsa.httpx,
        "AsyncClient",
        MockFITSClient,
    )

    result = asyncio.run(
        download_fits_product(
            "https://irsa.ipac.caltech.edu/test.fits",
            "TEST_001",
        )
    )

    downloaded_file = Path(result["path"])

    assert result["status"] == "downloaded"
    assert result["obs_id"] == "TEST_001"
    assert downloaded_file.exists()
    assert downloaded_file.read_bytes().startswith(b"SIMPLE  =")
    assert result["size_bytes"] == 2880


def test_download_fits_rejects_invalid_obs_id():
    import asyncio

    with pytest.raises(ValueError, match="obs_id"):
        asyncio.run(
            download_fits_product(
                "https://irsa.ipac.caltech.edu/test.fits",
                "",
            )
        )


def test_download_fits_rejects_http_url():
    import asyncio

    with pytest.raises(ValueError, match="Untrusted"):
        asyncio.run(
            download_fits_product(
                "http://irsa.ipac.caltech.edu/test.fits",
                "TEST_001",
            )
        )
