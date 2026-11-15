
from pathlib import Path

import pytest

from app.providers.wcs_wave import get_spectral_info


FITS_PATH = next(
    Path("temp").glob("2025W37_1A_0290_1*.fits")
)


def test_spectral_info_at_control_point():
    result = get_spectral_info(
        FITS_PATH,
        x=1021,
        y=1021,
    )

    assert result["source"] == "WCS-WAVE"
    assert result["method"] == "bilinear_interpolation"

    assert result["spectral_info"]["central_wavelength_um"] == pytest.approx(
        0.90429854
    )

    assert result["spectral_info"]["bandwidth_um"] == pytest.approx(
        0.02298692
    )


def test_spectral_info_at_arbitrary_pixel():
    result = get_spectral_info(
        FITS_PATH,
        x=1000,
        y=800,
    )

    assert result["spectral_info"]["central_wavelength_um"] == pytest.approx(
        0.946455,
        abs=1e-5,
    )


def test_reject_out_of_bounds_pixel():
    with pytest.raises(ValueError):
        get_spectral_info(
            FITS_PATH,
            x=2041,
            y=800,
        )


def test_reject_invalid_coordinate():
    with pytest.raises(ValueError):
        get_spectral_info(
            FITS_PATH,
            x=float("nan"),
            y=800,
        )
